import os
import sys
import datetime as dt


sys.path.insert(0, os.path.abspath(".."))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
]
source_suffix = '.rst'
master_doc = 'index'

project = u'Confuse'
copyright = '2012-{}, Adrian Sampson & contributors'.format(
    dt.date.today().year
)

version = '1.7'
release = '1.7.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

# -- Options for HTML output --------------------------------------------------

html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'Confusedoc'
