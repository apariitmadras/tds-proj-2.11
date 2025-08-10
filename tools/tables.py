from __future__ import annotations
from typing import Iterable, Optional, List, Dict
import pandas as pd
__all__ = [
"normalize_headers", "find_col", "pick_table_by_keywords",
"to_money", "to_year", "build_canonical_columns"
]
def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
"""Flatten MultiIndex, stringify, lowercase+strip headers, in-place; return
df."""
if isinstance(df.columns, pd.MultiIndex):
cols = [' '.join(str(x) for x in t if x is not None) for t in
df.columns.to_flat_index()]
else:
cols = [str(c) for c in df.columns]
df.columns = [c.strip().lower() for c in cols]
return df
def find_col(cols: Iterable[str], must_have: Optional[Iterable[str]] = None,
any_of: Optional[Iterable[str]] = None) -> Optional[str]:
names = list(cols)
low = [str(c).lower() for c in names]
must = [t.lower() for t in (must_have or [])]
anyt = [t.lower() for t in (any_of or [])]
for i, c in enumerate(low):
if all(t in c for t in must) and (not anyt or any(t in c for t in
anyt)):
return names[i]
return None
def pick_table_by_keywords(tables: List[pd.DataFrame], require: List[Dict]) ->
Optional[pd.DataFrame]:
for t in tables:
df = t.copy()
normalize_headers(df)
ok = True
for rule in require:
mh = [x.lower() for x in (rule.get("must_have") or [])]
ao = [x.lower() for x in (rule.get("any_of") or [])]
hit = False
for col in df.columns:
cl = str(col).lower()
if all(m in cl for m in mh) and (not ao or any(a in cl for a in
ao)):
hit = True; break
if not hit:
ok = False; break
if ok:
return df
return None
def to_money(s):
s = ''.join(ch for ch in str(s) if ch.isdigit() or ch in '.,')
s = s.replace(',', '')
try:
return float(s)
except Exception:
return None
def to_year(s):
t = ''.join(ch if ch.isdigit() else ' ' for ch in str(s))
for part in t.split():
if len(part) == 4:
try:
y = int(part)
if 1900 <= y <= 2100:
return y
except Exception:
pass
return None
def build_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
"""Create _rank/_peak/_title/_gross/_year columns using header discovery and
 robust coercion. Also create safety aliases (gross/year/title/rank/peak) if
missing.
 Assumes headers already normalized.
 """
col_rank = find_col(df.columns, any_of=["rank"])
col_peak = find_col(df.columns, any_of=["peak"])
col_title = find_col(df.columns, any_of=["title","film","movie"])
col_gross = find_col(df.columns, must_have=["gross"],
any_of=["world","worldwide"])
col_year = find_col(df.columns, any_of=["year","release","date"])
df["_rank"] = pd.to_numeric(df[col_rank], errors="coerce") if col_rank else
None
df["_peak"] = pd.to_numeric(df[col_peak], errors="coerce") if col_peak else
None
df["_title"] = df[col_title].astype(str) if col_title else ""
df["_gross"] = df[col_gross].apply(to_money) if col_gross else None
if col_year:
df["_year"] = df[col_year].apply(to_year)
else:
df["_year"] = df["_title"].apply(to_year)
if col_gross and "gross" not in df.columns:
df["gross"] = df[col_gross]
if col_year and "year" not in df.columns:
df["year"] = df[col_year]
if col_title and "title" not in df.columns:
df["title"] = df[col_title]
if col_rank and "rank" not in df.columns:
df["rank"] = df[col_rank]
if col_peak and "peak" not in df.columns:
df["peak"] = df[col_peak]
return df
