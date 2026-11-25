import fitz
def extract_pdf(data):
 with fitz.open(stream=data,filetype='pdf') as doc:
  if doc.needs_pass: raise ValueError('Encrypted PDF: upload an unlocked copy.')
  return [{'number':i+1,'text':p.get_text()} for i,p in enumerate(doc)], dict(doc.metadata)
