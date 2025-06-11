import streamlit as st
from datetime import date
import os
import re

TEMPLATE_DIR = "../../data/cuad/template_contracts"

def extract_placeholders(template_text):
    """{{...}} içindeki tüm değişken adlarını döndürür"""
    return sorted(set(re.findall(r"\{\{(.*?)\}\}", template_text)))

def render_draft():
    st.title("📑 Smart Contract Draft Generator")

    agreement_files = {
        "Convertible Note Agreement": "convertible_note_agreement.txt",
        "Employment Agreement": "employment_agreement.txt",
        "Founder Agreement": "founder_agreement.txt",
        "Freelancer Agreement": "freelancer_agreement.txt",
        "Investment Agreement": "investment_agreement.txt",
        "Joint Venture Agreement": "join_venture_agreement.txt",
        "NDA Agreement": "nda_agreement.txt",
        "SAFE Agreement": "safe_agreement.txt",
        "Stock Option Agreement": "stock_option_agreement.txt",
    }

    selected_label = st.selectbox("📂 Select Agreement Type", list(agreement_files.keys()))
    file_name = agreement_files[selected_label]
    file_path = os.path.join(TEMPLATE_DIR, file_name)

    if not os.path.exists(file_path):
        st.error(f"Template not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()

    st.subheader("✍️ Fill in the following fields:")
    placeholders = extract_placeholders(template)
    user_inputs = {}

    for ph in placeholders:
        if "date" in ph.lower():
            user_inputs[ph] = st.date_input(ph.replace("_", " ").title(), value=date.today())
        elif "address" in ph.lower():
            user_inputs[ph] = st.text_area(ph.replace("_", " ").title())
        else:
            user_inputs[ph] = st.text_input(ph.replace("_", " ").title())

    if st.button("📄 Generate Draft"):
        draft = template
        for key, value in user_inputs.items():
            formatted = value.strftime("%B %d, %Y") if isinstance(value, date) else str(value)
            draft = draft.replace(f"{{{{{key}}}}}", formatted)

        st.markdown("### 📜 Generated Contract")
        st.text_area("Preview", draft, height=600)

        st.download_button(
            label="📥 Download Contract as TXT",
            data=draft,
            file_name=f"{file_name.replace('.txt', '')}_draft.txt",
            mime="text/plain"
        )
