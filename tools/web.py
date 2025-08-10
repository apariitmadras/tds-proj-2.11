from __future__ import annotations
import requests
import pandas as pd
from typing import List, Optional
from .tables import pick_table_by_keywords
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MultiModelDataAgent/
1.0)"}
def fetch_text(url: str, timeout: int = 20) -> str:
resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
resp.raise_for_status()
return resp.text
def read_html_tables(url: str) -> List[pd.DataFrame]:
"""Return DataFrames parsed from HTML tables at `url`. Uses bs4 flavor.
 Falls back to fetching HTML first if needed.
 """
try:
return pd.read_html(url, flavor="bs4")
except Exception:
html = fetch_text(url)
return pd.read_html(html, flavor="bs4")
def read_table_by_keywords(url: str, require: list) -> Optional[pd.DataFrame]:
"""Read tables from `url` and return the first one whose normalized headers
 satisfy all `require` rules, where each rule is a dict like
 {"must_have":[...], "any_of":[...]}
 """
tables = read_html_tables(url)
return pick_table_by_keywords(tables, require=require)
