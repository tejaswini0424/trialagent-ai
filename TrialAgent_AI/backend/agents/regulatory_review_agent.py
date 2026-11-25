from config.regulatory_checklist import load_checklist
from backend.document_processing.text_processor import evidence
from backend.analysis.finding_classifier import finding
def run(doc,context):
 checklist=context.get('_checklist') or load_checklist();fs=[]
 for item in checklist['items']:
  matches=[evidence(doc,p) for p in item['patterns']];found=[x for x in matches if x[0]]
  status='Not Applicable' if item.get('not_applicable',False) else 'Present' if len(found)==len(matches) else 'Unclear' if found else 'Missing'
  e,p=found[0] if found else ('',None)
  f=finding('Regulatory Review',item['category'],item['category'],e,p,'Informational' if status in ['Present','Not Applicable'] else 'Medium',status,item['id'],item['requirement']+' '+item['guidance'])
  f.update(reference=item['reference'],reference_version=item['version']);fs.append(f)
 return {'findings':fs,'checklist':checklist,'summary':'Presence indicates keyword evidence only; adequacy and applicability require human review.'}
