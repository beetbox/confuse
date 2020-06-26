from __future__ import division, absolute_import, print_function


extensions = [
    'sphinx.ext.autosectionlabel',
]
source_suffix = '.rst'
master_doc = 'index'

project = u'Confuse'
copyright = u'2012, Adrian Sampson'

version = '1.2'
release = '1.2.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

# -- Options for HTML output --------------------------------------------------

html_theme = 'default'
htmlhelp_basename = 'Confusedoc'
