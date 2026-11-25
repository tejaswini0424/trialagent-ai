import re
def text_of(doc): return '\n'.join(p['text'] for p in doc['pages'])
def evidence(doc,pattern):
 for p in doc['pages']:
  for line in p['text'].splitlines():
   if re.search(pattern,line,re.I) and not re.search(r'not (?:supplied|provided|documented|available)|deliberate gaps|\bno (?:information|details|evidence)\b',line,re.I): return line.strip()[:900],p['number']
 return '',None
def lines(doc,pattern):
 return [(l.strip(),p['number']) for p in doc['pages'] for l in p['text'].splitlines() if re.search(pattern,l,re.I)]
