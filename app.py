
import streamlit as st
from core.processor import process_pdf

st.set_page_config(page_title="PEPCO PDF to CSV", layout="centered")

st.title("📄 PDF to CSV Exporter")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
export_set = st.selectbox("Select Export Set", [f"{i+1} Set{i+1}" for i in range(5)])
if st.button("Run & Export CSV") and uploaded_file:
    with st.spinner("Processing..."):
        csv_file = process_pdf(uploaded_file, export_set)
        if csv_file:
            st.success("Conversion complete!")
            st.download_button("📥 Download CSV", data=csv_file.getvalue(),
                               file_name="export.csv", mime="text/csv")
        else:
            st.error("Failed to process the PDF.")
