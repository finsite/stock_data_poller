"""Configuration file for the Sphinx documentation builder.

This file contains a selection of common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys

# -- Path setup -----------------------------------------------------
# Add the project root directory to the Python path to allow Sphinx to find the source code.
sys.path.insert(0, os.path.abspath("../.."))  # includes `src/`

# -- Project information --------------------------------------------
# Define basic project information.
project = "stock_data_poller"
copyright = "2025, Mark Quinn"
author = "Mark Quinn"
release = "0.1"

# -- General configuration ------------------------------------------
# Add Sphinx extensions for documentation generation.
extensions = [
    "sphinx.ext.autodoc",  # Pull in docstrings from code
    "sphinx.ext.napoleon",  # Support for Google/NumPy-style docstrings
    "sphinx.ext.viewcode",  # Adds "View Source" links
    "sphinx.ext.intersphinx",  # Links to external documentation
    "sphinx.ext.autosummary",  # Generates summary tables for modules/classes
    "sphinx_autodoc_typehints",  # Includes type hints in docstrings
]

# Automatically generate autosummary pages.
autosummary_generate = True

# Define external documentation for intersphinx to link to.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Optional: Treat missing references as warnings/errors.
# nitpicky = True

# Specify template paths.
templates_path = ["_templates"]

# Define patterns to exclude from the build.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ----------------------------------------
# Choose a theme for HTML output. You can change to 'sphinx_rtd_theme' if you prefer.
html_theme = "furo"
html_static_path = ["_static"]
