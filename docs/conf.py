import datetime as dt
import os
import sys

version = "2.3"
release = "2.3.0"

sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]
source_suffix = ".rst"
master_doc = "index"

project = "Confuse"
copyright = f"2012-{dt.date.today().year}, Adrian Sampson & contributors"

exclude_patterns = ["_build"]

pygments_style = "sphinx"

# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "Confusedoc"
