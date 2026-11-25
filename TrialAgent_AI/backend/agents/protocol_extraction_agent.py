import re
from pydantic import BaseModel, Field
from backend.document_processing.text_processor import evidence,lines,text_of
class Protocol(BaseModel):
 title:str='Not found'; objectives:list[str]=Field(default_factory=list); phase:str='Not found'; sponsor:str='Not found'; population:str='Not found'; inclusion_criteria:list[str]=Field(default_factory=list); exclusion_criteria:list[str]=Field(default_factory=list); sample_size:list[str]=Field(default_factory=list); duration:str='Not found'; endpoints:list[str]=Field(default_factory=list); treatment_arms:list[str]=Field(default_factory=list); dosage:list[str]=Field(default_factory=list)
def run(doc,context):
 data={}
 for key,pat in {'title':r'^(study title|title)\s*:', 'phase':r'phase\s+[1-4IV]+','sponsor':r'^sponsor','population':r'^population|study population','duration':r'duration|follow.up'}.items(): data[key]=evidence(doc,pat)[0] or 'Not found'
 for key,pat in {'objectives':r'objective','inclusion_criteria':r'^inclusion|^include:', 'exclusion_criteria':r'^exclusion|^exclude:', 'sample_size':r'sample size|enroll|participants|subjects', 'endpoints':r'endpoint','treatment_arms':r'arm|placebo|control group','dosage':r'\bmg\b|dosage|dose.*daily'}.items(): data[key]=[l for l,p in lines(doc,pat)]
 # Capture numbered/bulleted eligibility sections as well as explicit labels.
 for key,heading in [('inclusion_criteria','inclusion'),('exclusion_criteria','exclusion')]:
  active=False
  for line in text_of(doc).splitlines():
   if re.match(heading+r' criteria\s*:?$',line.strip(),re.I): active=True;continue
   if active:
    if re.match(r'^\s*(?:[-*•]|\d+[.)])',line): data[key].append(line.strip())
    elif line.strip(): active=False
 return {'protocol':Protocol(**data).model_dump(),'findings':[],'summary':'Extracted explicit protocol text; absent values remain unknown.'}
