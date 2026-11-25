import json,os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
import streamlit as st
import pandas as pd
from backend.authentication.auth import register,login
from backend.database.db_operations import documents,get_document,save_document,save_analysis,history
from backend.document_processing.document_loader import load_document
from backend.orchestration.orchestrator import analyze
from backend.orchestration.workflow import NAMES,PURPOSES
from frontend.components import findings_table,severity_chart,workflow_chart
from config.settings import DISCLAIMER
from config.regulatory_checklist import load_checklist
PAGES=['Overview Dashboard','Upload Clinical Protocol','Protocol Analysis','Multi-Agent Activity','Study Design Review','Eligibility Criteria Review','Safety and Risk Review','Regulatory Compliance Review','Consistency Validation','Findings Explorer','Document Viewer','Reports and Downloads','Analysis History','Settings']
def authentication():
 st.markdown('<div class="hero"><div class="tag">Local research intelligence</div><h1>TrialAgent AI</h1><p>Seven specialized agents. One evidence-grounded protocol review.</p></div>',unsafe_allow_html=True)
 left,right=st.columns([1,1])
 with left:
  st.subheader('Welcome back')
  with st.form('login'):
   username=st.text_input('Username');password=st.text_input('Password',type='password');submitted=st.form_submit_button('Login',type='primary')
  if submitted:
   uid=login(username,password)
   if uid: st.session_state.update(user_id=uid,username=username);st.rerun()
   else: st.error('Invalid username or password.')
 with right:
  st.subheader('Create your research account')
  with st.form('registration'):
   name=st.text_input('Username',key='new_user');pw=st.text_input('Password',type='password',key='new_pw');confirmation=st.text_input('Confirm password',type='password');create=st.form_submit_button('Create Account')
  if create:
   try: register(name,pw,confirmation);st.success('Account created. Log in to continue.')
   except ValueError as e: st.error(str(e))
 st.caption(DISCLAIMER)
def dashboard():
 if 'user_id' not in st.session_state: authentication();return
 uid=st.session_state.user_id
 with st.sidebar:
  st.markdown('## ◈ TrialAgent AI');st.caption('CLINICAL RESEARCH WORKSPACE')
  page=st.radio('Workspace',PAGES,label_visibility='collapsed')
  st.divider();st.caption('Offline analysis · Private local storage')
  if st.button('Logout',width='stretch'):
   st.session_state.clear();st.rerun()
 now=datetime.now(ZoneInfo(os.getenv('APP_TIMEZONE','Asia/Kolkata')))
 st.title('TrialAgent AI — Clinical Trial Protocol Intelligence')
 st.caption(f"{now.day} {now.strftime('%B %Y')} · {now.strftime('%H:%M:%S %Z')} · Signed in as {st.session_state.username}")
 st.markdown(f'<div class="hero"><div class="tag">Protocol intelligence / Research guidance</div><h2>{escape(page)}</h2><p>Trace findings to document evidence. Keep professional judgment at the center.</p></div>',unsafe_allow_html=True)
 docs=documents(uid);analyses=[json.loads(d.analysis) for d in docs if d.analysis]
 if page=='Upload Clinical Protocol':
  st.caption('PDF, DOCX or UTF-8 TXT · Maximum 20 MB · Scanned PDFs need OCR before upload')
  uploaded=st.file_uploader('Drop your clinical protocol here',type=['pdf','docx','txt'])
  sample=st.checkbox('Use synthetic demonstration protocol')
  if st.button('Analyze protocol',type='primary',disabled=not(uploaded or sample)):
   try:
    name='sample_protocol.txt' if sample else uploaded.name;data=(Path(__file__).resolve().parents[1]/'data/sample_protocol.txt').read_bytes() if sample else uploaded.getvalue()
    doc=load_document(name,data);did,duplicate=save_document(uid,doc)
    if duplicate: st.info('Duplicate detected: using your existing document record. This review replaces its latest results and adds a history entry.')
    progress=st.progress(0);status=st.empty()
    def update(name,state,fraction): progress.progress(fraction);status.write(f'{name} · {state}')
    result=analyze(doc,update,st.session_state.get('checklist'));save_analysis(uid,did,result);st.session_state.selected_document=did;st.success('Review saved. Open Protocol Analysis or Reports and Downloads.')
   except Exception as e: st.error(f'Analysis could not complete: {e}')
  st.download_button('Download synthetic protocol',(Path(__file__).resolve().parents[1]/'data/sample_protocol.txt').read_bytes(),'sample_protocol.txt')
  return
 if page=='Settings':
  st.write(DISCLAIMER);st.caption('No external model or API is used. The checklist can be edited as JSON; changes here apply to future reviews in this session.')
  current=st.session_state.get('checklist') or load_checklist()
  raw=st.text_area('Research checklist JSON',json.dumps(current,indent=2),height=350)
  if st.button('Validate and apply checklist'):
   try:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
     path=Path(tmp)/'checklist.json';path.write_text(raw,encoding='utf-8');st.session_state.checklist=load_checklist(path)
    st.success('Checklist validated and applied to future analyses.')
   except Exception as e: st.error(str(e))
  return
 if page=='Overview Dashboard':
  allf=[f for a in analyses for f in a['findings']];signals=[f for f in allf if f['status']!='Present'];logs=[l for a in analyses for l in a['agents']]
  values=[len(analyses),len(allf),sum(f['severity']=='Critical' for f in signals),sum(f['severity']=='High' for f in signals),sum(a['status']=='Completed' for a in analyses),f"{100*sum(l['status']=='Completed' for l in logs)/len(logs):.1f}%" if logs else '0%']
  for col,label,value in zip(st.columns(3),['Documents analyzed','Total findings','Critical findings'],values[:3]): col.metric(label,value)
  for col,label,value in zip(st.columns(3),['High-priority findings','Completed reviews','Agent execution success'],values[3:]): col.metric(label,value)
  left,right=st.columns(2)
  with left: st.subheader('Severity distribution');severity_chart(allf)
  with right: st.subheader('Recent documents');st.dataframe([{'Document':d.filename,'Status':d.status,'Uploaded':d.uploaded_at} for d in docs],hide_index=True,width='stretch')
  if not docs: st.info('Start with Upload Clinical Protocol and use the synthetic example or your own document.')
  return
 if page=='Analysis History':
  st.dataframe([{'Analysis':h.id,'Document':h.document_id,'Date (UTC)':h.created_at,'Summary':h.summary} for h in history(uid)],hide_index=True,width='stretch');return
 if not docs: st.info('Upload a protocol to begin.');return
 ids=[d.id for d in docs];default=st.session_state.get('selected_document',ids[0]);default=default if default in ids else ids[0]
 did=st.selectbox('Document',ids,index=ids.index(default),format_func=lambda i:next(d.filename+' · #'+str(i) for d in docs if d.id==i));st.session_state.selected_document=did
 record=get_document(uid,did);doc=json.loads(record.content);a=json.loads(record.analysis) if record.analysis else None
 if page=='Document Viewer':
  st.json({'filename':record.filename,'type':record.file_type,'metadata':doc['metadata'],'status':record.status})
  for p in doc['pages']:
   st.subheader('Page '+str(p['number']) if p['number'] else 'Extracted text · Pagination unavailable')
   safe=escape(p['text'])
   if a:
    excerpts=sorted({f['evidence'] for f in a['findings'] if f['evidence'] and f['evidence'] in p['text']},key=len,reverse=True)
    for excerpt in excerpts[:30]: safe=safe.replace(escape(excerpt),'<mark>'+escape(excerpt)+'</mark>')
   st.markdown('<pre style="white-space:pre-wrap">'+safe+'</pre>',unsafe_allow_html=True)
  if a: findings_table(a['findings'],'viewer')
  return
 if not a: st.info('Document has no completed analysis. Analyze it from the upload page.');return
 if page=='Protocol Analysis':
  st.write(a['report']['executive_summary']);st.json(a['results'].get('Protocol Extraction',{}).get('protocol',{}));severity_chart(a['findings']);st.caption(a['report']['limitations'])
 elif page=='Multi-Agent Activity':
  workflow_chart()
  for i,(name,purpose) in enumerate(zip(NAMES,PURPOSES)):
   log=next((l for l in a['agents'] if l['agent']==name),{'status':'Pending','duration':0,'output':{}})
   with st.container(border=True):
    st.subheader(f"{i+1:02} · {name} · {log['status']}");st.caption(purpose);st.write(f"{log['duration']:.3f} seconds · {len(log['output'].get('findings',[]))} findings");st.write(log['output'].get('summary','No output'))
    with st.expander('Execution log, inputs and outputs'): st.json(log)
 elif page=='Findings Explorer': findings_table(a['findings'])
 elif page=='Reports and Downloads':
  from backend.reports.pdf_generator import pdf_report
  from backend.reports.csv_generator import csv_report
  st.write(a['report']['executive_summary']);cols=st.columns(3)
  cols[0].download_button('↓ PDF review',pdf_report(doc,a),'trialagent_review.pdf','application/pdf')
  cols[1].download_button('↓ Findings CSV',csv_report(a),'trialagent_findings.csv','text/csv')
  cols[2].download_button('↓ Structured JSON',json.dumps({'document':doc,'analysis':a},indent=2),'trialagent_analysis.json','application/json')
  st.caption(a['report']['limitations'])
 else:
  mapping={'Study Design Review':'Study Design','Eligibility Criteria Review':'Eligibility','Safety and Risk Review':'Safety Review','Regulatory Compliance Review':'Regulatory Review','Consistency Validation':'Consistency'}
  result=a['results'].get(mapping[page],{});st.write(result.get('summary','Agent output unavailable; inspect execution logs.'))
  details={k:v for k,v in result.items() if k not in ['findings','summary']}
  if details:
   with st.expander('Structured agent output',expanded=True): st.json(details)
  findings_table(result.get('findings',[]),mapping[page])
