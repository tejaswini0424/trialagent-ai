import json,re
from pathlib import Path
def load_checklist(path=None):
 data=json.loads(Path(path or Path(__file__).resolve().parents[1]/'data/regulatory_checklist.json').read_text(encoding='utf-8'))
 return validate_checklist(data)
def validate_checklist(data):
 if not isinstance(data,dict) or not data.get('name') or not data.get('version') or not isinstance(data.get('items'),list): raise ValueError('Checklist needs name, version and items.')
 if not data['items']: raise ValueError('Checklist must contain items.')
 for i in data['items']:
  for key in ['id','category','requirement','reference','version','guidance','patterns']: 
   if key not in i: raise ValueError(f'Missing checklist field: {key}')
  if not i['patterns']: raise ValueError('Checklist patterns cannot be empty')
  for p in i['patterns']: re.compile(p)
 return data
