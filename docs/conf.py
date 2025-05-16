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

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'nbsphinx',
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

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
