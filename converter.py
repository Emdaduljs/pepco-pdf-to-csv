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

    if len(df) > 1:
        # Set first row as header
        headers = df.iloc[0].tolist()
        headers = make_unique(headers)
        df.columns = headers
        df = df[1:].reset_index(drop=True)

    return df

def make_unique(seq):
    seen = {}
    result = []
    for item in seq:
        if item in seen:
            seen[item] += 1
            new_item = f"{item}_{seen[item]}"
        else:
            seen[item] = 0
            new_item = item
        result.append(new_item if new_item else "Unnamed")
    return result
