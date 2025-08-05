
import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe
from gsheet import upload_to_gsheet

st.set_page_config(page_title="Cuda Automation CSV Converter from PDF", layout="centered")

st.markdown("""
    <style>
        .password-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
        }
        .logo-box img {
            margin-top: 10px;
            width: 149px;
            height: 332px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Cuda Automation CSV Converter from PDF")

with st.sidebar:
    st.markdown('<div class="password-box">🔐 <b>Enter Password</b></div>', unsafe_allow_html=True)
    role = st.radio("Login as", ["Editor", "User"])
    input_password = st.text_input("Password", type="password")
    st.markdown('<div class="logo-box"><img src="https://raw.githubusercontent.com/emdadulhaque2009/pepco-streamlit-assets/main/ui_logo.png"></div>', unsafe_allow_html=True)

if (role == "Editor" and input_password != "123") or (role == "User" and input_password != "1234"):
    st.error("Invalid password.")
else:
    uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")
    spreadsheet_url = st.text_input("🔗 Google Spreadsheet URL")
    st.markdown("🔒 Data will always export to tab: **Sheet3**")

    if uploaded_pdf and spreadsheet_url:
        with st.spinner("⏳ Processing PDF..."):
            df = parse_pdf_to_dataframe(uploaded_pdf)
            st.success("✅ PDF parsed successfully!")
            st.dataframe(df)

            if st.button("📤 Export to Google Sheet + Download CSV"):
                upload_to_gsheet(df, spreadsheet_url, "Sheet3")
                csv_name = uploaded_pdf.name.replace(".pdf", ".csv")
                df.to_csv(csv_name, index=False)
                st.success("✅ Exported to Sheet3 and CSV generated!")
                with open(csv_name, "rb") as f:
                    st.download_button("⬇️ Download CSV", f, file_name=csv_name)
