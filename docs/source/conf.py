import os
import sys

# -- Path setup -----------------------------------------------------
# Add the project root's 'src' directory to the Python path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "src"))
print(f"[INFO] Sphinx sys.path includes: {SRC_PATH}")
sys.path.insert(0, SRC_PATH)

# -- Project information --------------------------------------------
project = "stock_data_poller"
copyright = "2025, Mark Quinn"
author = "Mark Quinn"
release = "0.1"

# -- General configuration ------------------------------------------
extensions = [
    # "sphinx.ext.autodoc",
    # "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.autosummary",  # Commented out to avoid autosummary errors
    # "sphinx_autodoc_typehints",
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
