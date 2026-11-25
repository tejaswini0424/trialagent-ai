from backend.document_processing.text_processor import evidence
from backend.analysis.finding_classifier import finding
def run(doc,context):
 fields={'allocation':r'non.randomized|randomized|randomised','masking':r'double.blind|single.blind|open.label','control':r'placebo|control group|active comparator','primary endpoint':r'primary endpoint','secondary endpoint':r'secondary endpoint','sample size justification':r'power|sample size.*(justif|calcul)'}
 out={};fs=[]
 for label,pat in fields.items():
  e,p=evidence(doc,pat);out[label]=e or 'Not found'
  if not e: fs.append(finding('Study Design',f'{label.capitalize()} not located','Study design',status='Missing'))
 return {'details':out,'findings':fs,'summary':f'{len(fs)} study design documentation items need review.'}
