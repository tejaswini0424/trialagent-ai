from backend.document_processing.text_processor import evidence
from backend.analysis.finding_classifier import finding
def run(doc,context):
 fs=[];details={}
 for label,pat in {'Safety monitoring':r'safety monitor','Adverse event reporting':r'adverse event.*report','Serious adverse event reporting':r'(serious adverse|SAE).*report','Stopping rules':r'stopping|stop.*rule','Safety committee':r'DSMB|data safety|safety committee'}.items():
  e,p=evidence(doc,pat);details[label]=e or 'Not found'
  if not e: fs.append(finding('Safety Review',label+' text not located','Safety',severity='High' if 'Serious' in label or 'Stopping' in label else 'Medium',status='Missing',description='Relevant text was not detected; this does not establish non-compliance.'))
 return {'details':details,'findings':fs,'summary':f'{len(fs)} safety documentation items require manual review.'}
