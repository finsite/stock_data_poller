# """
# Configuration file for the Sphinx documentation builder.

# This file contains a selection of common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# """

# import os
# import sys

# # -- Path setup -----------------------------------------------------
# # Add the project root directory to the Python path to allow Sphinx to find the source code.
# SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
# sys.path.insert(0, SRC_PATH)

# # -- Project information --------------------------------------------
# # Define basic project information.
# project = "stock_data_poller"
# copyright = "2025, Mark Quinn"
# author = "Mark Quinn"
# release = "0.1"

# # -- General configuration ------------------------------------------
# # Add Sphinx extensions for documentation generation.
# extensions = [
#     "sphinx.ext.autodoc",  # Pull in docstrings from code
#     "sphinx.ext.napoleon",  # Support for Google/NumPy-style docstrings
#     "sphinx.ext.viewcode",  # Adds "View Source" links
#     "sphinx.ext.intersphinx",  # Links to external documentation
#     # "sphinx.ext.autosummary",  # Generates summary tables for modules/classes
#     "sphinx_autodoc_typehints",  # Includes type hints in docstrings
# ]

# # Automatically generate autosummary pages.
# #autosummary_generate = True

# # Define external documentation for intersphinx to link to.
# intersphinx_mapping = {
#     "python": ("https://docs.python.org/3", None),
#     "requests": ("https://docs.python-requests.org/en/latest/", None),
#     "pandas": ("https://pandas.pydata.org/docs/", None),
# }

# # Optional: Treat missing references as warnings/errors.
# # nitpicky = True

# # Specify template paths.
# templates_path = ["_templates"]

# # Define patterns to exclude from the build.
# exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# # -- Options for HTML output ----------------------------------------
# # Choose a theme for HTML output. You can change to 'sphinx_rtd_theme' if you prefer.
# html_theme = "furo"
# html_static_path = ["_static"]
# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup -----------------------------------------------------
# Add the project root's 'src' directory to the Python path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src"))
print(f"✅ Sphinx sys.path includes: {SRC_PATH}")
sys.path.insert(0, SRC_PATH)

# -- Project information --------------------------------------------
project = "stock_data_poller"
copyright = "2025, Mark Quinn"
author = "Mark Quinn"
release = "0.1"

# -- General configuration ------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.autosummary",  # Commented out to avoid autosummary errors
    "sphinx_autodoc_typehints",
]

# Optional: if you *do* want autosummary back later
# autosummary_generate = False

# Optional: ignore missing modules if still having trouble
# autodoc_mock_imports = ["src", "pollers", "message_queue"]

# Intersphinx mappings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output ---------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
