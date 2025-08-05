
import pdfplumber
import pandas as pd
from io import BytesIO

def parse_pdf_to_dataframe(file):
    with pdfplumber.open(BytesIO(file.read())) as pdf:
        all_data = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_data.extend(table)
        if not all_data:
            return pd.DataFrame()
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        return df
