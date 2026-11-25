import csv
from io import StringIO
def csv_report(analysis):
 rows=analysis['findings'];output=StringIO()
 fields=list(dict.fromkeys(k for row in rows for k in row)) or ['title','severity','description','evidence']
 writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader()
 for row in rows:
  safe={k:("'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v) for k,v in row.items()}
  writer.writerow(safe)
 return output.getvalue().encode('utf-8-sig')
