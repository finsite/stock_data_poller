# -- Path setup -----------------------------------------------------
# This is necessary so Sphinx can find the source code relative to this
# configuration file.
import os
import sys

# sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("../.."))  # includes `src/`

# -- Project information --------------------------------------------
project = "stock_data_poller"
copyright = "2025, Mark Quinn"
author = "Mark Quinn"
release = "0.1"

# -- General configuration ------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # Pull in docstrings from code
    "sphinx.ext.napoleon",  # Support for Google/NumPy-style docstrings
    "sphinx.ext.viewcode",  # Adds "View Source" links
    "sphinx.ext.intersphinx",  # Links to external documentation
    "sphinx.ext.autosummary",  # Generates summary tables for modules/classes
    "sphinx_autodoc_typehints",  # Includes type hints in docstrings
]

# Automatically generate autosummary pages
autosummary_generate = True

# External docs for intersphinx to link to
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Optional: Treat missing references as warnings/errors
# nitpicky = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ----------------------------------------
html_theme = "furo"  # You can change to 'sphinx_rtd_theme' if you prefer
html_static_path = ["_static"]
