import streamlit as st
import pdfplumber
import pandas as pd

st.set_page_config(page_title="PDF Table Extractor", layout="wide")
st.title("📄 PDF Table Extractor - Custom Headers")

# Upload PDF
uploaded_pdf = st.file_uploader("Upload PDF file with the table", type="pdf")

if uploaded_pdf:
    # Save uploaded PDF temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_pdf.read())

    try:
        with pdfplumber.open("temp.pdf") as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    # Convert to DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # You might want to strip whitespace from columns & rows
                    df.columns = [str(c).strip() for c in df.columns]
                    df = df.applymap(lambda x: str(x).strip() if x else x)
                    
                    # Rename columns to your custom headers if count matches
                    # Adjust if your PDF headers differ in count/order
                    if len(df.columns) == 8:
                        df.columns = [
                            "Order - ID",
                            "Item No",
                            "Supplier product code",
                            "Colour 6/9",
                            "9/12",
                            "12/18",
                            "18/24",
                            "24/36"
                        ]
                        all_tables.append(df)
                    else:
                        st.warning("A table with unexpected number of columns found and skipped.")
            
            if all_tables:
                final_df = pd.concat(all_tables, ignore_index=True)
                st.subheader("Extracted Table")
                st.dataframe(final_df, use_container_width=True)

                csv = final_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download as CSV",
                    data=csv,
                    file_name="extracted_table.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No tables with expected format found in the PDF.")
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
else:
    st.info("Upload a PDF file to extract tables.")
