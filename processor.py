
import fitz  # PyMuPDF
import pandas as pd

def extract_tables_with_custom_headers(pdf_path):
    doc = fitz.open(pdf_path)
    all_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        lines = sorted([b for b in blocks if b[4].strip()], key=lambda b: (b[1], b[0]))
        rows = []

        for line in lines:
            row_text = line[4].strip()
            if row_text:
                row = row_text.split()
                rows.append(row)

        for row in rows:
            if len(row) >= 7:
                fixed_data = row[:7]
                sku_data = row[7:]
                row_dict = {
                    "Order ID": fixed_data[0],
                    "ID": fixed_data[1],
                    "Item No": fixed_data[2],
                    "Item classification": fixed_data[3],
                    "Supplier product code": fixed_data[4],
                    "Merch code": fixed_data[5],
                    "Supplier name": fixed_data[6],
                }
                for i, sku in enumerate(sku_data):
                    row_dict[f"SKU No {i + 1}"] = sku
                all_data.append(row_dict)

    df = pd.DataFrame(all_data)
    return df
