import fitz  # PyMuPDF
import pandas as pd

def parse_pdf_to_dataframe(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    rows = []
    for page in doc:
        lines = page.get_text().split('\n')
        for line in lines:
            parts = line.strip().split()
            if parts:
                rows.append(parts)
    doc.close()

    # Normalize row length
    max_len = max(len(r) for r in rows)
    data = [r + [""] * (max_len - len(r)) for r in rows]

    df = pd.DataFrame(data)

    # Optionally use first row as header
    if len(df) > 1:
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

    return df
