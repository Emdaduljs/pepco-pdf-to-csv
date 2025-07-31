import streamlit as st

st.title("PDF Table Extraction")

uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")

if uploaded_pdf:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    
    # Extract table as above
    with pdfplumber.open("temp.pdf") as pdf:
        tables = []
        for page in pdf.pages:
            for table in page.extract_tables():
                df = pd.DataFrame(table[1:], columns=table[0])
                df.columns = [
                    "Order - ID", "Item No", "Supplier product code", 
                    "Colour 6/9", "9/12", "12/18", "18/24", "24/36"
                ]
                tables.append(df)
        
        final_df = pd.concat(tables, ignore_index=True)
    
    st.subheader("Extracted Table")
    st.dataframe(final_df)

    st.download_button(
        label="Download CSV",
        data=final_df.to_csv(index=False).encode("utf-8"),
        file_name="extracted_table.csv",
        mime="text/csv"
    )
