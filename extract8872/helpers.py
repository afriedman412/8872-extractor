import os
import re
import tempfile
import zipfile
from typing import Any, Literal, Tuple, Union

import pandas as pd
import pdfplumber
from flask import session


def extract_one_page(page: pdfplumber.page.Page) -> Tuple[
    Any,
    Literal['a', 'b', 'x']
]:
    page_text = page.extract_text()
    data: list[Union[list[str], tuple[str, str]]] = []
    schedule: Literal['a', 'b', 'x'] = 'x'
    if page_text.startswith("Contributor"):
        entries = [e for e in page.extract_text().split(
            "Contributor'sname,mailingaddressandZIPcode Nameofcontributor'semployer") if e]

        for e_ in entries:
            name = e_.split("\n")[1].split(" ")[0]
            cash_search = re.search(
                r"\$\s?\d+(?:[\d\/]+)",
                e_.split("\n")[5]
            )
            if cash_search is not None:
                cash = cash_search[0].replace(" ", "")
            else:
                cash = "$0"
            data.append((name, cash))
        schedule = 'a'
        del page_text

    elif page_text.startswith("Recipient'sname"):
        entries = [
            e for e in page.extract_text().split(
                "Recipient'sname,mailingaddressandZIPcode Nameofrecipient'semployer AmountofExpenditure"
            ) if e]

        for e_ in entries:
            name_cash = e_.split("\n")[1].replace("$ ", "$").split(" ")
            name_cash = [name_cash[0], name_cash[-1], e_.split("\n")[5]]
            data.append(name_cash)
        schedule = 'b'
        del page_text
    return data, schedule


def extract_one_file(p: pdfplumber.pdf.PDF) -> None:
    for page in p.pages:
        data, schedule = extract_one_page(page)
        if data:
            df = make_df(data, schedule)
            df.to_csv(session.get(schedule), mode="a+")
        del data
    del p
    return


def establish_files() -> None:
    temp_dir = tempfile.mkdtemp()
    for schedule in "ab":
        data_type = "contributions" if schedule == 'a' else "expenses"
        df = pd.DataFrame()
        file_path = os.path.join(
            temp_dir, f"{session.get('file_name')}_{schedule}_{data_type}.csv")
        df.to_csv(os.path.join(temp_dir, file_path))
        session[schedule] = file_path
    session['archive'] = os.path.join(
        temp_dir, session.get('file_name', "NO_FILE_NAME")+".zip")


def compress_files() -> None:
    try:
        with zipfile.ZipFile(session['archive'], "w") as zip:
            for schedule in 'ab':
                zip.write(
                    session.get(schedule, ""),
                    arcname=session.get(schedule, "").split("/")[-1]
                )
    except IndexError:
        raise IndexError("Archive file doesn't exist!")
    return


def make_df(
        data: list[Any],
        schedule: Literal['a', 'b', 'x']
) -> pd.DataFrame:
    columns = ["Contributor", "Amount"] if schedule == 'a' else [
        'Recipient', 'Amount', 'Purpose']
    df = pd.DataFrame(data, columns=columns)
    return df
