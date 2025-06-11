import streamlit as st
from tools.utils import write_message
from app.agents.agent import generate_response

def render_chat():
    st.title("💬 Legal Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I'm the Legal Chatbot! How can I help you?"},
        ]

    def handle_submit(message):
        with st.spinner('Thinking...'):
            response = generate_response(message)
            write_message('assistant', response)

    for message in st.session_state.messages:
        write_message(message['role'], message['content'], save=False)

    if prompt := st.chat_input("Ask me anything legal-related..."):
        write_message('user', prompt)
        handle_submit(prompt)
