from typing import Literal
from pydantic import BaseModel, Field
Severity=Literal['Critical','High','Medium','Low','Informational']
Status=Literal['Present','Missing','Unclear','Needs Human Review','Not Applicable']
class Finding(BaseModel):
 title:str; description:str; severity:Severity='Medium'; category:str
 evidence:str=''; page:int|None=None; checklist_id:str|None=None
 suggested_action:str='Verify the original document and resolve with a qualified reviewer.'
 agent:str; status:Status='Needs Human Review'; section:str=''
def finding(agent,title,category,evidence='',page=None,severity='Medium',status='Needs Human Review',checklist_id=None,description=None):
 return Finding(agent=agent,title=title,category=category,evidence=evidence,page=page,severity=severity,status=status,checklist_id=checklist_id,section=category,description=description or title).model_dump()
