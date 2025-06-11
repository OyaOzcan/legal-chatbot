import streamlit as st
from app.interfaces.streamlit.chat_tab import render_chat
from app.interfaces.streamlit.analyze_tab import render_analysis
from app.interfaces.streamlit.draft_tab import render_draft
st.set_page_config(
    page_title="LexMind",     # 🧠 Sekmede görünen başlık
    page_icon="⚖️",                 # 🖼 Emoji ya da favicon
)
# Sidebar
st.sidebar.title("📚 Legal Assistant")
section = st.sidebar.radio("Choose Mode", ["💬 Chat", "📄 Analyze Contract", "📝 Draft Generator"])

# Route to corresponding module
if section == "💬 Chat":
    render_chat()

elif section == "📄 Analyze Contract":
    render_analysis()

elif section == "📝 Draft Generator":
    render_draft()
