import datetime as dt
import os
import re
import sys
from pathlib import Path

MATCH_VERSION_LINE = re.compile(r"version = \W((\d+\.\d+)\.\d.*?)\W").fullmatch

pyproject = Path(__file__).parent.parent / "pyproject.toml"
version_line_match = next(
    filter(None, map(MATCH_VERSION_LINE, pyproject.read_text().splitlines()))
)
release, version = version_line_match.groups()

sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx_rtd_theme",
]
source_suffix = ".rst"
master_doc = "index"

project = "Confuse"
copyright = "2012-{}, Adrian Sampson & contributors".format(dt.date.today().year)

exclude_patterns = ["_build"]

pygments_style = "sphinx"

# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "Confusedoc"
