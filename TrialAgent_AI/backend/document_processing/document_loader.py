from pathlib import Path
from io import BytesIO
from hashlib import sha256
from docx import Document
from config.settings import MAX_UPLOAD_MB
from backend.document_processing.pdf_extractor import extract_pdf
def load_document(filename,data):
 ext=Path(filename).suffix.lower()
 if ext not in {'.pdf','.docx','.txt'}: raise ValueError('Unsupported format. Use PDF, DOCX or TXT.')
 if not data or len(data)>MAX_UPLOAD_MB*1024*1024: raise ValueError('Empty file or upload size limit exceeded.')
 try:
  if ext=='.pdf': pages,metadata=extract_pdf(data)
  elif ext=='.docx':
   doc=Document(BytesIO(data)); text='\n'.join([p.text for p in doc.paragraphs]+[' | '.join(c.text for c in r.cells) for t in doc.tables for r in t.rows]);pages=[{'number':None,'text':text}]; metadata={'title':doc.core_properties.title}
  else: pages=[{'number':None,'text':data.decode('utf-8-sig')}];metadata={}
 except Exception as exc: raise ValueError(f'Cannot extract document: {exc}') from exc
 if not any(p['text'].strip() for p in pages): raise ValueError('No extractable text. Scanned PDFs require OCR, which is not included.')
 return {'filename':Path(filename).name,'file_type':ext,'digest':sha256(data).hexdigest(),'pages':pages,'metadata':metadata}
