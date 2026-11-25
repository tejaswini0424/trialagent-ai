import json,fitz
from backend.orchestration.orchestrator import analyze
from backend.reports.pdf_generator import pdf_report
from backend.reports.csv_generator import csv_report
def test_pdf_report(sample):
 a=analyze(sample);data=pdf_report(sample,a);assert data.startswith(b'%PDF');pdf=fitz.open(stream=data,filetype='pdf');text=''.join(p.get_text() for p in pdf);assert 'TrialAgent' in text;assert 'Limitations' in text;assert 'Evidence:' in text
 assert len(pdf)>1
def test_csv_json(sample):
 a=analyze(sample);csv=csv_report(a).decode('utf-8-sig');assert 'severity' in csv;assert 'Different enrollment' in csv;assert json.loads(json.dumps(a))['status']=='Completed'
def test_csv_formula_escape():
 assert "'=HYPERLINK" in csv_report({'findings':[{'evidence':'=HYPERLINK(1)'}]}).decode('utf-8-sig')
