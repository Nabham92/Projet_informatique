import streamlit as st
from recommendations import show_recommendations
from visualizations import show_visualizations
import os

# Back-end URL
if os.getenv("DOCKER_ENV") == "true":
    BACKEND_URL = "http://backend:8000"
else:
    BACKEND_URL = "http://localhost:8000"
st.set_page_config(page_title="🎬 Recommandations de Films", layout="wide")
#st.write("🚨 dashboard.py chargé")

with st.sidebar.expander("🔧 Info débogage"):
    st.write(f"URL back-end : {BACKEND_URL}")

st.title("🎬 Système de Recommandation de Films")
tab1, tab2 = st.tabs(["🔍 Recommandations", "📊 Statistiques"])

with tab1:
    try:
        show_recommendations()
    except Exception as e:
        st.error("❌ show_recommendations a planté")
        st.exception(e)

with tab2:
    try:
        show_visualizations()
    except Exception as e:
        st.error("❌ show_visualizations a planté")
        st.exception(e)
