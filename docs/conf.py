#!/usr/bin/env python
# vim: set et sw=4 sts=4:

# Copyright 2014-2015 Dave Hughes <dave@waveform.org.uk>.
#
# This file is part of umansysprop.
#
# umansysprop is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# umansysprop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# umansysprop.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import umansysprop as app

# -- General configuration ------------------------------------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.intersphinx']
templates_path = ['_templates']
source_suffix = '.rst'
#source_encoding = 'utf-8-sig'
master_doc = 'index'
project = app.__project__.title()
copyright = '2014-2015 %s' % app.__author__
version = app.__version__
release = app.__version__
#language = None
#today_fmt = '%B %d, %Y'
exclude_patterns = ['_build']
#default_role = None
#add_function_parentheses = True
#add_module_names = True
#show_authors = False
pygments_style = 'sphinx'
#modindex_common_prefix = []
#keep_warnings = False

# -- Autodoc configuration ------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Intersphinx configuration --------------------------------------------

intersphinx_mapping = {
    'python': ('http://docs.python.org/3.2', None),
    'numpy':  ('http://docs.scipy.org/doc/numpy/', None),
    }

# -- Options for HTML output ----------------------------------------------

html_theme = 'default'
#html_theme_options = {}
#html_theme_path = []
#html_title = None
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
#html_extra_path = []
#html_last_updated_fmt = '%b %d, %Y'
#html_use_smartypants = True
#html_sidebars = {}
#html_additional_pages = {}
#html_domain_indices = True
#html_use_index = True
#html_split_index = False
#html_show_sourcelink = True
#html_show_sphinx = True
#html_show_copyright = True
#html_use_opensearch = ''
#html_file_suffix = None
htmlhelp_basename = '%sdoc' % app.__project__

# Hack to make wide tables work properly in RTD
# See https://github.com/snide/sphinx_rtd_theme/issues/117 for details
def setup(app):
    app.add_stylesheet('style_override.css')

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    #'preamble': '',
}

latex_documents = [
    (
        'index',                       # source start file
        '%s.tex' % app.__project__,    # target filename
        '%s Documentation' % project,  # title
        app.__author__,                # author
        'manual',                      # documentclass
        ),
]

#latex_logo = None
#latex_use_parts = False
#latex_show_pagerefs = False
#latex_show_urls = False
#latex_appendices = []
#latex_domain_indices = True

# -- Options for manual page output ---------------------------------------

man_pages = []

#man_show_urls = False

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = []

#texinfo_appendices = []
#texinfo_domain_indices = True
#texinfo_show_urls = 'footnote'
#texinfo_no_detailmenu = False
