from backend.analysis.explanation_generator import explain
def run(doc,context):
 findings=[f for name,out in context.items() if not name.startswith('_') for f in out.get('findings',[])]
 return {'findings':[],'report':explain(context,findings),'summary':'Consolidated evidence-grounded research review.'}
