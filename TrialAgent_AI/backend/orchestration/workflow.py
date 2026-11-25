NAMES=['Protocol Extraction','Study Design','Eligibility','Safety Review','Regulatory Review','Consistency','Report Generation']
PURPOSES=['Extract explicit protocol fields','Review allocation, masking and endpoints','Screen eligibility wording','Review safety documentation','Evaluate configurable research checklist','Compare document statements','Consolidate review and explanations']
def graph():
 import networkx as nx
 g=nx.DiGraph();g.add_edges_from(zip(['Ingestion']+NAMES,NAMES+['Report']));return g
