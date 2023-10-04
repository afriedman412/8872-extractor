import pdfplumber
import pandas as pd
from typing import Literal
import re
import tempfile
import os
import zipfile

def extract_one_page(page):
    page_text = page.extract_text()
    if page_text.startswith("Contributor"):
        entries = [e for e in page.extract_text().split(
            "Contributor'sname,mailingaddressandZIPcode Nameofcontributor'semployer") if e]

        data = []
        for e_ in entries:
            name = e_.split("\n")[1].split(" ")[0]
            if re.search(r"\$\s?\d+(?:[\d\/]+)", e_.split("\n")[5]):
                cash = re.search(r"\$\s?\d+(?:[\d\/]+)", e_.split("\n")[5])[0].replace(" ", "")
            else:
                cash = "$0"
            data.append((name, cash))
        return data, 'a'
    
    elif page_text.startswith("Recipient'sname"):
        entries = [
            e for e in page.extract_text().split(
        "Recipient'sname,mailingaddressandZIPcode Nameofrecipient'semployer AmountofExpenditure") if e]

        data = []
        for e_ in entries:
            name_cash = e_.split("\n")[1].replace("$ ", "$").split(" ")
            name_cash = [name_cash[0], name_cash[-1], e_.split("\n")[5]]
            data.append(name_cash)
        return data, 'b'
    else:
        return None, False
    
def extract_one_file(
    p: pdfplumber.pdf.PDF,
    track_pages: bool=False
):
    data_out = {
        "a": [],
        "b": []
    }
    for n, page in enumerate(p.pages):
        if track_pages:
            print(n)
        data, schedule = extract_one_page(page)
        if data:
            data_out[schedule]+=(data)
    return data_out

def create_files(data_out, file_name):
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    for schedule, data in data_out.items():
        data_type = "contributions" if schedule == 'a' else "expenses"
        df = make_df(data, schedule)
        file_path = os.path.join(temp_dir, f"{file_name}_{schedule}_{data_type}.csv")
        df.to_csv(os.path.join(temp_dir, file_path))
        file_paths.append(file_path)

    arc_path = os.path.join(temp_dir, file_name+".zip")
    with zipfile.ZipFile(arc_path, "w") as zip:
        for file_path in file_paths:
            zip.write(file_path, arcname=file_path.split("/")[-1])
    return arc_path

def make_df(
        data: list,
        schedule: Literal['a', 'b']
        ):
    columns = ["Contributor", "Amount"] if schedule=='a' else ['Recipient', 'Amount', 'Purpose']
    df = pd.DataFrame(data, columns=columns)
    return df
    