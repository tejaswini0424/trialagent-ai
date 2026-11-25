from collections import Counter
from config.settings import DISCLAIMER
def explain(results,findings):
 counts=Counter(f['severity'] for f in findings if f['status']!='Present')
 sections={name:out.get('summary','No summary available.') for name,out in results.items() if isinstance(out,dict)}
 return {'executive_summary':f"Review identified {sum(counts.values())} documentation review signals. Severity distribution: {dict(counts)}. These are screening results, not a determination of regulatory compliance.",'sections':sections,'human_review':[f['title'] for f in findings if f['status']!='Present'],'limitations':DISCLAIMER+' Local rules do not interpret clinical validity, infer omitted content, or perform OCR.'}
