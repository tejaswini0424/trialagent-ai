import os,json,secrets,threading
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI,Request,Response,HTTPException,UploadFile,File,Depends
from fastapi.responses import HTMLResponse,FileResponse
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from sqlalchemy.exc import SQLAlchemyError
from backend.database.db_connection import initialize
from backend.authentication.auth import register,login
from backend.database.db_operations import documents,get_document,save_document,save_analysis,history
from backend.document_processing.document_loader import load_document
from backend.orchestration.orchestrator import analyze
from backend.reports.pdf_generator import pdf_report
from backend.reports.csv_generator import csv_report
from config.regulatory_checklist import load_checklist
from config.settings import DISCLAIMER,DATABASE_URL
BASE=Path(__file__).resolve().parent
CLOUD=bool(os.getenv('VERCEL'))
SECRET=os.getenv('SESSION_SECRET')
if CLOUD and (not SECRET or DATABASE_URL.startswith('sqlite')): raise RuntimeError('Set SESSION_SECRET and a hosted PostgreSQL DATABASE_URL before deployment.')
serializer=URLSafeTimedSerializer(SECRET or secrets.token_hex(32),salt='trialagent-session-v1')
app=FastAPI(title='TrialAgent AI',docs_url=None,redoc_url=None)
_ready=False;_lock=threading.Lock()
def ready():
 global _ready
 if not _ready:
  with _lock:
   if not _ready: initialize();_ready=True
@app.middleware('http')
async def security(request,call_next):
 if request.method in ['POST','PUT','PATCH','DELETE']:
  origin=request.headers.get('origin')
  if origin and urlparse(origin).netloc!=request.headers.get('host'): return Response('Cross-origin request rejected',status_code=403)
  size=request.headers.get('content-length','0')
  if size.isdigit() and int(size)>4*1024*1024: return Response('Maximum web upload/request size is 4 MB.',status_code=413)
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff';response.headers['X-Frame-Options']='DENY';response.headers['Referrer-Policy']='same-origin';response.headers['Cache-Control']='no-store'
 response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'self'; frame-ancestors 'none'"
 return response
@app.exception_handler(SQLAlchemyError)
async def database_error(request,exc):
 return Response(json.dumps({'detail':'Database unavailable. Please retry.'}),status_code=503,media_type='application/json')
def user(request:Request):
 ready();token=request.cookies.get('trialagent_session')
 try: return serializer.loads(token or '',max_age=8*60*60)
 except (BadSignature,SignatureExpired): raise HTTPException(401,'Please log in.')
class Credentials(BaseModel):
 username:str;password:str;confirmation:str|None=None
@app.get('/',response_class=HTMLResponse)
def home(): return (BASE/'index.html').read_text(encoding='utf-8')
@app.get('/assets/{name}')
def asset(name:str):
 if name not in ['app.js','style.css']: raise HTTPException(404)
 return FileResponse(BASE/name,media_type='text/javascript' if name.endswith('.js') else 'text/css')
@app.get('/api/health')
def health(): return {'status':'ok','application':'TrialAgent AI','storage':'PostgreSQL' if not DATABASE_URL.startswith('sqlite') else 'SQLite (local only)'}
@app.post('/api/register')
def registration(data:Credentials):
 ready()
 try: register(data.username,data.password,data.confirmation or '');return {'message':'Account created. Log in to continue.'}
 except ValueError as e: raise HTTPException(400,str(e))
@app.post('/api/login')
def signin(data:Credentials,response:Response):
 ready();uid=login(data.username,data.password)
 if not uid: raise HTTPException(401,'Invalid username or password.')
 response.set_cookie('trialagent_session',serializer.dumps({'id':uid,'username':data.username}),httponly=True,secure=CLOUD,samesite='strict',max_age=8*60*60,path='/')
 return {'username':data.username}
@app.post('/api/logout')
def logout(response:Response): response.delete_cookie('trialagent_session',path='/');return {'message':'Logged out'}
@app.get('/api/me')
def me(u=Depends(user)): return {'username':u['username'],'disclaimer':DISCLAIMER}
@app.get('/api/documents')
def listing(u=Depends(user)):
 return [{'id':d.id,'filename':d.filename,'uploaded_at':d.uploaded_at.isoformat(),'status':d.status,'analysis':json.loads(d.analysis) if d.analysis else None} for d in documents(u['id'])]
@app.get('/api/documents/{did}')
def detail(did:int,u=Depends(user)):
 try: d=get_document(u['id'],did)
 except PermissionError: raise HTTPException(404,'Document not available.')
 return {'id':d.id,'document':json.loads(d.content),'analysis':json.loads(d.analysis) if d.analysis else None}
class Options(BaseModel):
 checklist:dict|None=None

def perform(doc,u,checklist=None):
 if checklist:
  try:
   from config.regulatory_checklist import validate_checklist
   validate_checklist(checklist)
  except Exception as e: raise HTTPException(400,'Invalid checklist: '+str(e))
 did,duplicate=save_document(u['id'],doc);a=analyze(doc,checklist=checklist);save_analysis(u['id'],did,a)
 return {'id':did,'duplicate':duplicate,'status':a['status']}
@app.post('/api/analyze')
async def upload(file:UploadFile=File(...),u=Depends(user)):
 data=await file.read(4*1024*1024+1)
 if len(data)>4*1024*1024: raise HTTPException(413,'Maximum web upload size is 4 MB.')
 try: doc=load_document(file.filename or '',data)
 except ValueError as e: raise HTTPException(400,str(e))
 # CPU-bound review executes in a worker thread, without blocking the event loop.
 from starlette.concurrency import run_in_threadpool
 return await run_in_threadpool(perform,doc,u)
@app.post('/api/sample')
def sample(options:Options,u=Depends(user)):
 root=BASE.parent
 return perform(load_document('sample_protocol.txt',(root/'data/sample_protocol.txt').read_bytes()),u,options.checklist)
@app.post('/api/documents/{did}/reanalyze')
def reanalyze(did:int,options:Options,u=Depends(user)):
 try: d=get_document(u['id'],did)
 except PermissionError: raise HTTPException(404,'Document not available.')
 return perform(json.loads(d.content),u,options.checklist)
@app.get('/api/checklist')
def checklist(u=Depends(user)): return load_checklist()
@app.get('/api/history')
def review_history(u=Depends(user)):
 return [{'id':h.id,'document_id':h.document_id,'date':h.created_at.isoformat(),'summary':h.summary} for h in history(u['id'])]
@app.get('/api/documents/{did}/export/{kind}')
def export(did:int,kind:str,u=Depends(user)):
 try: d=get_document(u['id'],did)
 except PermissionError: raise HTTPException(404,'Document not available.')
 if not d.analysis: raise HTTPException(400,'Document has no analysis.')
 a=json.loads(d.analysis);doc=json.loads(d.content)
 if kind=='pdf': data=pdf_report(doc,a);mime='application/pdf'
 elif kind=='csv': data=csv_report(a);mime='text/csv'
 elif kind=='json': data=json.dumps({'document':doc,'analysis':a},indent=2).encode();mime='application/json'
 else: raise HTTPException(404)
 return Response(data,media_type=mime,headers={'Content-Disposition':f'attachment; filename="trialagent_review.{kind}"'})
