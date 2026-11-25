import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.database.db_connection import Session
from backend.database.models import Document,AgentResult,FindingRecord,AnalysisHistory
def documents(user_id):
 with Session() as s: return list(s.scalars(select(Document).where(Document.user_id==user_id).order_by(Document.id.desc())))
def get_document(user_id,document_id):
 with Session() as s:
  d=s.scalar(select(Document).where(Document.id==document_id,Document.user_id==user_id))
  if not d: raise PermissionError('Document not available.')
  return d
def save_document(user_id,doc):
 with Session() as s:
  old=s.scalar(select(Document).where(Document.user_id==user_id,Document.digest==doc['digest']))
  if old: return old.id,True
  d=Document(user_id=user_id,filename=doc['filename'],file_type=doc['file_type'],digest=doc['digest'],content=json.dumps(doc));s.add(d)
  try: s.commit()
  except IntegrityError:
   s.rollback(); old=s.scalar(select(Document).where(Document.user_id==user_id,Document.digest==doc['digest']));return old.id,True
  return d.id,False
def save_analysis(user_id,document_id,analysis):
 get_document(user_id,document_id)
 with Session() as s:
  d=s.get(Document,document_id);d.analysis=json.dumps(analysis);d.status=analysis['status']
  for cls in [AgentResult,FindingRecord]:
   for old in s.scalars(select(cls).where(cls.document_id==document_id)): s.delete(old)
  for a in analysis['agents']: s.add(AgentResult(document_id=document_id,agent_name=a['agent'],status=a['status'],duration=a['duration'],output=json.dumps(a)))
  for f in analysis['findings']: s.add(FindingRecord(document_id=document_id,agent_name=f['agent'],severity=f['severity'],category=f['category'],description=f['description'],evidence=f['evidence'],page=f['page'],review_status=f['status'],payload=json.dumps(f)))
  s.add(AnalysisHistory(user_id=user_id,document_id=document_id,summary=analysis['report']['executive_summary']));s.commit()
def history(user_id):
 with Session() as s: return list(s.scalars(select(AnalysisHistory).where(AnalysisHistory.user_id==user_id).order_by(AnalysisHistory.id.desc())))
