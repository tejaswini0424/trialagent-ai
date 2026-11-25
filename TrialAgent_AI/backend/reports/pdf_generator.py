from io import BytesIO
from html import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime,timezone
from reportlab.lib.colors import HexColor
from config.settings import DISCLAIMER
def pdf_report(doc,analysis):
 buf=BytesIO();styles=getSampleStyleSheet();story=[]
 for name in ['Title','Heading1','Heading2','Heading3']: styles[name].textColor=HexColor('#123c51')
 def add(text,style='BodyText'):
  story.append(Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style]));
  if style=='BodyText': story.append(Spacer(1,8))
 add('TrialAgent AI — Research Protocol Review','Title');add(doc['filename'],'Heading1');add('Generated '+datetime.now(timezone.utc).isoformat());add(str(doc.get('metadata',{})));add(analysis['report']['executive_summary'])
 for name,summary in analysis['report']['sections'].items(): add(name,'Heading2');add(summary)
 add('Protocol overview','Heading2')
 for key,value in analysis['results'].get('Protocol Extraction',{}).get('protocol',{}).items(): add(key.replace('_',' ').title()+': '+str(value))
 from collections import Counter
 add('Severity distribution','Heading2');add(str(dict(Counter(f['severity'] for f in analysis['findings'] if f['status']!='Present'))))
 add('Agent execution','Heading2')
 for a in analysis['agents']: add(f"{a['agent']}: {a['status']} ({a['duration']:.3f}s); attempts {a['attempts']}")
 add('Findings and checklist evidence','Heading2')
 for f in analysis['findings']:
  add(f"{f['severity']} / {f['status']} — {f['title']}",'Heading3');add(f['description']);add('Evidence: '+(f['evidence'] or 'No matching text located')+(' | Page '+str(f['page']) if f['page'] else ''));add('Agent: '+f['agent']+' | Checklist: '+str(f.get('checklist_id') or '—'));add(f.get('reference',''));add('Suggested action: '+f['suggested_action'])
 add('Limitations','Heading2');add(analysis['report']['limitations']);add(DISCLAIMER)
 def footer(canvas,document):
  canvas.setFont('Helvetica',8);canvas.drawString(36,24,'TrialAgent AI | Research guidance');canvas.drawRightString(560,24,f'Page {document.page}')
 SimpleDocTemplate(buf,title='TrialAgent AI Review').build(story,onFirstPage=footer,onLaterPages=footer);return buf.getvalue()
