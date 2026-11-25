import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from backend.orchestration.workflow import graph
COLORS={'Critical':'#ff4267','High':'#ff916c','Medium':'#efcc65','Low':'#63a9fa','Informational':'#35d7bc'}
def findings_table(findings,key='findings'):
 if not findings: st.info('No findings for this selection.');return
 df=pd.DataFrame(findings);cols=st.columns(4)
 for col,field in zip(cols,['severity','agent','category','status']):
  selected=col.multiselect(field.replace('_',' ').title(),sorted(df[field].unique()),key=key+field)
  if selected: df=df[df[field].isin(selected)]
 search=st.text_input('Search findings and evidence',key=key+'search')
 if search: df=df[df.astype(str).apply(lambda row:row.str.contains(search,case=False,regex=False).any(),axis=1)]
 st.dataframe(df[['severity','title','agent','category','status','page']],width='stretch',hide_index=True)
 if not df.empty:
  selected=st.selectbox('Finding details',list(df.index),format_func=lambda i:f"{df.loc[i,'severity']} · {df.loc[i,'title']}",key=key+'detail')
  f=df.loc[selected];st.write(f['description']);st.code(f['evidence'] or 'No matching text located',language=None);st.caption(f"Page: {f['page'] if pd.notna(f['page']) else 'Unavailable'} · Checklist: {f['checklist_id'] or '—'}");st.write(f['suggested_action'])
 from backend.reports.csv_generator import csv_report
 st.download_button('Export filtered findings',csv_report({'findings':df.to_dict('records')}),'filtered_findings.csv','text/csv',key=key+'export')
def severity_chart(findings):
 if not findings: return
 df=pd.DataFrame(findings);df=df[df.status!='Present']
 if df.empty: return
 counts=df.groupby('severity').size().reset_index(name='count')
 fig=px.pie(counts,names='severity',values='count',hole=.68,color='severity',color_discrete_map=COLORS)
 fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#e7f0fa',margin=dict(t=20,b=20));st.plotly_chart(fig,width='stretch')
def workflow_chart():
 g=graph();pos=nx.spring_layout(g,seed=7)
 fig=go.Figure()
 for a,b in g.edges:
  fig.add_trace(go.Scatter(x=[pos[a][0],pos[b][0]],y=[pos[a][1],pos[b][1]],mode='lines',line=dict(color='#2d6e86'),hoverinfo='skip',showlegend=False))
 fig.add_trace(go.Scatter(x=[pos[n][0] for n in g],y=[pos[n][1] for n in g],text=list(g),mode='markers+text',textposition='top center',marker=dict(size=18,color='#35d7bc'),showlegend=False))
 fig.update_layout(height=420,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#e7f0fa',xaxis=dict(visible=False),yaxis=dict(visible=False));st.plotly_chart(fig,width='stretch')
