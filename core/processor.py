
import os
import subprocess
from io import BytesIO
import pandas as pd

def process_pdf(uploaded_file, export_set):
    temp_pdf_path = f"temp_{export_set}.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # This assumes you use Excel macros to extract tables
    # Save to template.xlsm sheet and run Excel silently (Windows only)
    try:
        output_csv = f"output_{export_set}.csv"
        subprocess.run(["excel", "assets/template.xlsm", "/e", f"/mMacro{export_set}"], check=True)
        if os.path.exists(output_csv):
            with open(output_csv, "rb") as f:
                return BytesIO(f.read())
    except Exception as e:
        print("Error:", e)
    return None
