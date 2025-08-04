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

        # Sort vertically by y0 (top coordinate)
        items.sort(key=lambda i: i["y0"])

        # Group into rows by y0 proximity
        rows = []
        current_row = []
        last_y = None

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

        # Sort each row's items by x-coordinate
        table_data = []
        for row in rows:
            sorted_row = sorted(row, key=lambda i: i["x0"])
            table_data.append([cell["text"] for cell in sorted_row])

        all_rows.extend(table_data)

    doc.close()

    # Normalize column lengths
    max_len = max(len(r) for r in all_rows)
    normalized = [r + [""] * (max_len - len(r)) for r in all_rows]
    df = pd.DataFrame(normalized)

    # Set header if data is valid
    if len(df) > 1:
        headers = make_unique(df.iloc[0].tolist())
        df.columns = headers
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
            new_item = f"{item}_{seen[item]}"
        else:
            seen[item] = 0
            new_item = item
        result.append(new_item)
    return result
import fitz  # PyMuPDF
import pandas as pd

def parse_pdf_to_dataframe_bounding_boxes(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    rows = []
    for page in doc:
        blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, "text", block_no, block_type)
        # Sort blocks by y0 (top to bottom), then x0 (left to right)
        blocks.sort(key=lambda b: (b[1], b[0]))

        page_rows = []
        for b in blocks:
            text = b[4].strip()
            if text:
                # Split lines inside block
                lines = text.split('\n')
                for line in lines:
                    parts = line.split()
                    if parts:
                        page_rows.append(parts)
        rows.extend(page_rows)
    doc.close()

    # Normalize row length
    max_len = max(len(r) for r in rows) if rows else 0
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
