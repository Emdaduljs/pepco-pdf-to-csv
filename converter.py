import fitz  # PyMuPDF
import pandas as pd

def extract_tables_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_tables = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                rows = []
                for l in b["lines"]:
                    row = [s["text"].strip() for s in l["spans"] if s["text"].strip()]
                    if row:
                        rows.append(row)
                if rows:
                    df = pd.DataFrame(rows)
                    all_tables.append(df)

    doc.close()

    # Normalize and clean all tables
    cleaned_tables = []
    for table in all_tables:
        if table.shape[0] < 2:
            continue  # skip if not a proper table
        header = table.iloc[0].str.upper().str.strip()
        data = table.iloc[1:].reset_index(drop=True)
        data.columns = header
        cleaned_tables.append(data)

    if cleaned_tables:
        return pd.concat(cleaned_tables, ignore_index=True)
    return pd.DataFrame()
