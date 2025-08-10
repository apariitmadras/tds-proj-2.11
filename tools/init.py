# Re-export helpers for convenience in generated scripts
from .web import fetch_text, read_html_tables, read_table_by_keywords
from .tables import (
    normalize_headers,
    find_col,
    pick_table_by_keywords,
    to_money,
    to_year,
    build_canonical_columns,
)
from .plot import scatter_with_regression_base64
