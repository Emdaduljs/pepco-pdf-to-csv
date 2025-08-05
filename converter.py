import fitz  # PyMuPDF
import pandas as pd

def parse_pdf_to_dataframe_bounding_boxes(pdf_file, y_tolerance=5):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_rows = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        items = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        items.append({
                            "text": span["text"],
                            "x0": span["bbox"][0],
                            "y0": span["bbox"][1],
                            "x1": span["bbox"][2],
                            "y1": span["bbox"][3],
                        })

        items.sort(key=lambda i: i["y0"])
        rows, current_row, last_y = [], [], None

        for item in items:
            y = item["y0"]
            if last_y is None or abs(y - last_y) <= y_tolerance:
                current_row.append(item)
            else:
                rows.append(current_row)
                current_row = [item]
            last_y = y
        if current_row:
            rows.append(current_row)

        table_data = [[cell["text"] for cell in sorted(row, key=lambda i: i["x0"])] for row in rows]
        all_rows.extend(table_data)

    doc.close()

    # Normalize row lengths
    if not all_rows:
        return pd.DataFrame()
    max_len = max(len(r) for r in all_rows)
    normalized = [r + [""] * (max_len - len(r)) for r in all_rows]
    df = pd.DataFrame(normalized)

    # Find 'ORDER' and 'ITEM' row to use as header
    header_index = None
    for i, row in df.iterrows():
        if "ORDER" in row.values and "ITEM" in row.values:
            header_index = i
            break

    if header_index is not None:
        headers = make_unique(df.iloc[header_index].tolist())
        df.columns = headers
        df = df[header_index + 1:].reset_index(drop=True)
    else:
        df.columns = make_unique(df.iloc[0].tolist())
        df = df[1:].reset_index(drop=True)

    return df

def make_unique(seq):
    seen = {}
    result = []
    for item in seq:
        if not item:
            item = "Unnamed"
        if item in seen:
            seen[item] += 1
            item = f"{item}_{seen[item]}"
        else:
            seen[item] = 0
        result.append(item)
    return result
