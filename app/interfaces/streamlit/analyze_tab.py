import streamlit as st
import pdfplumber
import os

from app.agents.agent import generate_response  
from app.infrastructure.llm import llm

def check_essential_clauses(text: str):
    essential_checks = {
        "Parties": lambda t: "between" in t and "agreement" in t.lower(),
        "Effective Date": lambda t: "effective date" in t.lower() or "commencement" in t.lower(),
        "Purpose": lambda t: "purpose of this agreement" in t.lower() or "scope" in t.lower(),
        "Termination": lambda t: "termination" in t.lower() or "term of this agreement" in t.lower(),
        "Payment": lambda t: any(x in t.lower() for x in ["payment", "fee", "shall pay"]),
        "Delivery": lambda t: "delivery" in t.lower(),
        "Rights & Obligations": lambda t: "party" in t.lower() and "shall" in t.lower(),
        "Governing Law": lambda t: "governed by" in t.lower() or "jurisdiction" in t.lower(),
        "Confidentiality": lambda t: "confidential" in t.lower() or "non-disclosure" in t.lower(),
    }
    return [label for label, fn in essential_checks.items() if not fn(text)]

def extract_text_from_pdf(file) -> str:
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def render_analysis():
    st.header("📄 Contract Analysis – Missing Clauses")

    uploaded_file = st.file_uploader("Upload a contract (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[-1].lower()

        if file_ext == ".pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_ext == ".txt":
            text = uploaded_file.read().decode("utf-8")
        else:
            st.warning("Unsupported file type.")
            return

        st.subheader("🧠 Analyzing contract...")

        missing_clauses = check_essential_clauses(text)

        if missing_clauses:
            st.error("⚠️ Missing essential clauses found:")

            for clause in missing_clauses:
                st.markdown(f"- ❌ **{clause}**")

                if st.button(f"➕ Generate '{clause}' Clause"):
                    with st.spinner(f"Generating '{clause}' clause..."):
                        query = (
                            f"Generate a standard '{clause}' clause suitable for a startup contract."
                            f"\nHere is the contract text:\n{text[:1500]}..."
                        )
                        result = generate_response(query)

                    st.markdown(f"### 🤖 Suggested Clause for **{clause}**:")
                    st.markdown(result)
        else:
            st.success("✅ All essential clauses are present in this contract!")

        with st.expander("📜 Full Contract Text"):
            st.text_area("Contract Content", text, height=400)
