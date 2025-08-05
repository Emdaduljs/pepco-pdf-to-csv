import streamlit as st
import pandas as pd
from converter import parse_pdf_to_dataframe
from gsheet import upload_to_gsheet

# --- Page Config ---
st.set_page_config(page_title="Cuda Automation CSV converter from PDF", layout="wide")

# --- Password Authentication ---
col1, col2 = st.columns([1, 3])

with col1:
    st.image("ui_logo.png", width=149)  # Ensure ui_logo.png is in the same directory
    st.subheader("🔐 Login")

    password = st.text_input("Enter Password", type="password")
    role = None
    if password == "123":
        role = "editor"
    elif password == "1234":
        role = "user"
    else:
        if password:
            st.error("Incorrect password")

with col2:
    st.title("📄 Cuda Automation CSV converter from PDF")

    if role:
        # --- Source Selection ---
        sheet_choice = st.selectbox("Select Google Sheet Destination", ["Pepco", "Pep&co"])

        sheet_urls = {
            "Pepco": "https://docs.google.com/spreadsheets/d/1ug0VTy8iwUeSdpw4upHkVMxnwSekvYrxz6nm04_BJ-o/edit?usp=sharing",
            "Pep&co": "https://docs.google.com/spreadsheets/d/PLACE_YOUR_SECOND_URL_HERE"
        }

        selected_url = sheet_urls[sheet_choice]
        sheet_name = st.text_input("📝 Sheet Name (e.g., Sheet1)")

        uploaded_pdf = st.file_uploader("📁 Upload your PDF", type="pdf")

        if uploaded_pdf and sheet_name:
            try:
                df = parse_pdf_to_dataframe(uploaded_pdf)
                st.success("✅ PDF parsed successfully!")
                st.dataframe(df)

                if st.button("📤 Upload to Google Sheet"):
                    upload_to_gsheet(df, selected_url, sheet_name)
                    st.success("✅ Uploaded to Google Sheet!")
                    csv_name = f"{sheet_choice}_export.csv"
                    df.to_csv(csv_name, index=False)
                    st.download_button("⬇️ Download CSV", data=open(csv_name, "rb"), file_name=csv_name, mime="text/csv")

            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid password to continue.")
