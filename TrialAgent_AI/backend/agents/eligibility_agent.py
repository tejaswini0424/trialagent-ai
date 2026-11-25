import re
from backend.document_processing.text_processor import evidence
from backend.analysis.finding_classifier import finding
def run(doc,context):
 protocol=context.get('Protocol Extraction',{}).get('protocol',{});fs=[]
 for kind in ['inclusion_criteria','exclusion_criteria']:
  values=protocol.get(kind,[]);seen=set()
  if not values: fs.append(finding('Eligibility',f'{kind.replace("_"," ")} not located','Eligibility',status='Missing'))
  for value in values:
   norm=re.sub(r'[^a-z0-9]','',value.lower());e,p=evidence(doc,re.escape(value))
   if norm in seen: fs.append(finding('Eligibility','Duplicate eligibility criterion','Eligibility',e,p,'Low'))
   seen.add(norm)
   if re.search(r'adequate|appropriate|at discretion|healthy|significant',value,re.I): fs.append(finding('Eligibility','Ambiguous eligibility wording','Eligibility',e,p))
 inc=' '.join(protocol.get('inclusion_criteria',[]));exc=' '.join(protocol.get('exclusion_criteria',[]))
 for token in ['pregnant','diabetes','hypertension']:
  if token in inc.lower() and token in exc.lower(): fs.append(finding('Eligibility',f'Potential inclusion/exclusion overlap: {token}','Eligibility',inc+' | '+exc,severity='High'))
 # TF-IDF flags near duplicates for review; it does not decide equivalence.
 values=protocol.get('inclusion_criteria',[])+protocol.get('exclusion_criteria',[])
 if len(values)>1:
  try:
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.metrics.pairwise import cosine_similarity
   matrix=cosine_similarity(TfidfVectorizer(ngram_range=(1,2)).fit_transform(values))
   for i in range(len(values)):
    for j in range(i+1,len(values)):
     if .75<=matrix[i,j]<.999:
      fs.append(finding('Eligibility','Similar eligibility wording: verify duplication or overlap','Eligibility',values[i]+' | '+values[j],severity='Low'))
  except (ValueError,ImportError): pass
 return {'findings':fs,'criteria':{k:protocol.get(k,[]) for k in ['inclusion_criteria','exclusion_criteria']},'summary':f'{len(fs)} eligibility review signals. Overlap signals require interpretation.'}
