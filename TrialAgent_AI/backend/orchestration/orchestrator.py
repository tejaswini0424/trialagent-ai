import time, logging
from backend.agents import protocol_extraction_agent,study_design_agent,eligibility_agent,safety_review_agent,regulatory_review_agent,consistency_agent,report_agent
from backend.orchestration.workflow import NAMES
MODULES=[protocol_extraction_agent,study_design_agent,eligibility_agent,safety_review_agent,regulatory_review_agent,consistency_agent,report_agent]
def analyze(doc,callback=None,checklist=None,retries=1,modules=None):
 context={'_checklist':checklist} if checklist else {};logs=[]
 for name,module in zip(NAMES,modules or MODULES):
  inputs={'filename':doc['filename'],'upstream':list(context.keys())};started=time.perf_counter();status='Running';error=None;out={};attempt=0
  if callback: callback(name,status,len(logs)/7)
  if name=='Eligibility' and 'Protocol Extraction' not in context:
   status='Skipped';error='Protocol extraction unavailable.'
  else:
   for attempt in range(retries+1):
    try:
     out=module.run(doc,context);context[name]=out;status='Completed';break
    except Exception as exc:
     logging.exception('Agent %s failed, attempt %s',name,attempt+1);error=str(exc);status='Failed'
  logs.append({'agent':name,'status':status,'duration':time.perf_counter()-started,'attempts':attempt+1 if status!='Skipped' else 0,'error':error if status!='Completed' else None,'input':inputs,'output':out})
  if callback: callback(name,status,len(logs)/7)
 findings=[f for n,o in context.items() if not n.startswith('_') for f in o.get('findings',[])]
 from backend.analysis.explanation_generator import explain
 return {'results':{k:v for k,v in context.items() if not k.startswith('_')},'agents':logs,'findings':findings,'report':explain(context,findings),'status':'Completed' if all(l['status']=='Completed' for l in logs) else 'Partial'}
