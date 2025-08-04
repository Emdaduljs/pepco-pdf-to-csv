import fitz  # PyMuPDF
import pandas as pd

def extract_tables_from_pdf(file_path):
    doc = fitz.open(file_path)
    tables = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")

        # Sort by y-position to maintain row order
        blocks.sort(key=lambda b: (b[1], b[0]))

        rows = []
        for block in blocks:
            text = block[4].strip()
            if text:
                row = text.split()
                rows.append(row)

        if rows:
            # Use max column length for padding
            max_len = max(len(r) for r in rows)
            padded = [r + [""] * (max_len - len(r)) for r in rows]
            df = pd.DataFrame(padded)
            tables.append(df)

    return tables
