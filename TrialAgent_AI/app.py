import streamlit as st
from frontend.styles import CSS
from backend.database.db_connection import initialize
from frontend.dashboard import dashboard
st.set_page_config(page_title='TrialAgent AI',page_icon='◈',layout='wide')
st.markdown(CSS,unsafe_allow_html=True)
try:
 initialize();dashboard()
except Exception as exc:
 st.error(f'Application error: {exc}')
 st.caption('Check database permissions and configuration, then reload.')
