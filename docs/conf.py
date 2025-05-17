# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Meal Planner'
copyright = '2025, Yoshika Govender'
author = 'Yoshika Govender'
version = '1.0'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'nbsphinx',
    'sphinx.ext.viewcode',  # Add source links
    'sphinx.ext.intersphinx',  # Link to other project's documentation
]

# Configure nbsphinx to find notebooks in examples directory
nbsphinx_allow_directives = True
nbsphinx_kernel_name = 'python3'

# Add paths for finding source files
import shutil
examples_dir = os.path.abspath('../examples')
if os.path.exists('feature_overview.ipynb'):
    os.remove('feature_overview.ipynb')
shutil.copy2(os.path.join(examples_dir, 'feature_overview.ipynb'), 'feature_overview.ipynb')

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs', None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'prev_next_buttons_location': 'both',
    'style_external_links': True,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_with_keys': True,
}

html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# These paths are either relative to html_static_path or fully qualified paths (eg. https://...)
html_js_files = [
    'custom.js',
]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer.
html_show_copyright = True
