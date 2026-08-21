# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the source directory to the path so sphinx can find the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

project = 'lvpyioTools'
copyright = '2026, Simon Cadet'
author = 'Simon Cadet'
release = '2.4.3'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

# Theme
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'github_url': 'https://github.com/SimKDT/lvpyio-tools',
    'navbar_align': 'left',
}

# HTML output options
html_static_path = ['_static']
html_logo = None
html_title = 'lvpyioTools Documentation'

# Autodoc options
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'show-inheritance': True,
}

# Intersphinx mapping for cross-references
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}
