import re
from backend.document_processing.text_processor import lines
from backend.analysis.finding_classifier import finding
def run(doc,context):
 fs=[];sizes=[]
 for line,page in lines(doc,r'sample size|enroll'):
  match=re.search(r'(?:sample size\s*:?\s*|enroll(?:ment|ing)?\s*:?\s*)(\d+)',line,re.I)
  if match: sizes.append((int(match[1]),line,page))
 if len({s[0] for s in sizes})>1:
  fs.append(finding('Consistency','Different enrollment totals detected','Consistency',' | '.join(s[1] for s in sizes),sizes[0][2],'High'))
 dates=lines(doc,r'(start|end) date')
 parsed={}
 for line,p in dates:
  m=re.search(r'(start|end) date\s*:\s*(\d{4}-\d{2}-\d{2})',line,re.I)
  if m: parsed[m[1].lower()]=(m[2],line,p)
 if 'start' in parsed and 'end' in parsed and parsed['start'][0]>parsed['end'][0]: fs.append(finding('Consistency','Study end precedes start','Consistency',parsed['start'][1]+' | '+parsed['end'][1],severity='High'))
 primary=lines(doc,r'primary endpoint')
 normalized={re.sub(r'[^a-z0-9]','',re.sub(r'^.*?primary endpoint\s*:', '',l,flags=re.I).lower()) for l,p in primary}
 if len(normalized)>1: fs.append(finding('Consistency','Different primary endpoint descriptions','Endpoints',' | '.join(l for l,p in primary),primary[0][1],'High'))
 text='\n'.join(p['text'] for p in doc['pages'])
 for line,p in lines(doc,r'see section\s+\d'):
  for ref in re.findall(r'see section\s+(\d+(?:\.\d+)*)',line,re.I):
   if not re.search(r'^\s*(?:section\s+)?'+re.escape(ref)+r'[ .:]\s*\S',text,re.M|re.I): fs.append(finding('Consistency','Cross-reference target not located','Cross-references',line,p,'Low'))
 # Explicit objective/endpoint outcome terms only; semantic equivalence is not inferred.
 objectives=' '.join(context.get('Protocol Extraction',{}).get('protocol',{}).get('objectives',[])).lower()
 endpoints=' '.join(l for l,p in primary).lower()
 if objectives and endpoints:
  terms=['survival','blood pressure','quality of life','pain']
  if any(t in objectives for t in terms) and not any(t in objectives and t in endpoints for t in terms): fs.append(finding('Consistency','Objective and primary endpoint outcome terms differ','Endpoints',objectives+' | '+endpoints,severity='Medium'))
 for f in context.get('Eligibility',{}).get('findings',[]):
  if 'overlap' in f['title'].lower():
   copy=dict(f);copy['agent']='Consistency';copy['title']='Cross-section check: '+f['title'];fs.append(copy)
 return {'findings':fs,'sample_size_mentions':sizes,'summary':f'{len(fs)} consistency signals; semantic contradictions require manual review.'}
