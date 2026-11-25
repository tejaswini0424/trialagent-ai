import pytest,fitz
from io import BytesIO
from docx import Document
from backend.document_processing.document_loader import load_document
def test_txt(sample): assert sample['pages'][0]['number'] is None
@pytest.mark.parametrize('name,data',[('x.exe',b'hi'),('x.txt',b''),('x.pdf',b'broken'),('x.docx',b'broken'),('x.txt',b'   ')])
def test_invalid(name,data):
 with pytest.raises(ValueError): load_document(name,data)
def test_pdf():
 doc=fitz.open();doc.new_page().insert_text((72,72),'Study title: Test');doc.new_page().insert_text((72,72),'Safety monitoring: weekly')
 result=load_document('test.pdf',doc.tobytes());assert len(result['pages'])==2;assert result['pages'][1]['number']==2
 blank=fitz.open();blank.new_page()
 with pytest.raises(ValueError): load_document('blank.pdf',blank.tobytes())
def test_docx():
 doc=Document();doc.add_paragraph('Study title: Test');table=doc.add_table(rows=1,cols=1);table.cell(0,0).text='Sample size: 80';buf=BytesIO();doc.save(buf)
 out=load_document('test.docx',buf.getvalue());assert 'Sample size: 80' in out['pages'][0]['text'];assert out['pages'][0]['number'] is None
