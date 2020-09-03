from __future__ import division, absolute_import, print_function

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
]
source_suffix = '.rst'
master_doc = 'index'

project = u'Confuse'
copyright = u'2012, Adrian Sampson'

version = '1.3'
release = '1.3.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
htmlhelp_basename = 'Confusedoc'

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
