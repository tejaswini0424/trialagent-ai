"""Build an isolated deployment bundle from shared source; never copy local databases or secrets."""
from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.deploy'
DEST.mkdir(exist_ok=True)
for folder in ['backend','config','data','web']:
 for source in (ROOT/folder).rglob('*'):
  if source.is_file() and '__pycache__' not in source.parts and source.suffix not in ['.pyc','.db']:
   target=DEST/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
(DEST/'app.py').write_text('from web.api import app\n',encoding='utf-8')
shutil.copy2(ROOT/'requirements-web.txt',DEST/'requirements.txt')
(DEST/'.python-version').write_text('3.12\n')
(DEST/'vercel.json').write_text(json.dumps({'$schema':'https://openapi.vercel.sh/vercel.json','framework':'fastapi','functions':{'app.py':{'maxDuration':60}}},indent=2))
(DEST/'.vercelignore').write_text('.env*\n*.db\n__pycache__\n**/__pycache__/**\n')
print('Deployment source prepared at',DEST)
