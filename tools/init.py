# Convenience re-exports so generated code can do:
# from tools.tables import normalize_headers, find_col,
build_canonical_columns
# from tools.web import read_html_tables, read_table_by_keywords
# from tools.plot import scatter_with_regression_base64
from .tables import normalize_headers, find_col, build_canonical_columns,
to_money, to_year
from .web import read_html_tables, read_table_by_keywords, fetch_text
from .plot import scatter_with_regression_base64
