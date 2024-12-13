# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = u"sgfixedincome_pkg"
copyright = u"2024, Gideon Tay"
author = u"Gideon Tay"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Notebook execution settings
nb_execution_mode = "off"  # This will prevent notebook execution
nb_execution_raise_on_error = False

# Autoapi settings
autoapi_dirs = ["../src/sgfixedincome_pkg"] 
autoapi_ignore = ["*/streamlit_app/*"]  # Exclude streamlit_app
autoapi_output_dir = '_autoapi'  # Different output directory
autoapi_add_toctree_entry = True
autoapi_python_class_content = 'both'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build", "Thumbs.db", ".DS_Store", 
    "*streamlit_app*", "**streamlit_app**"
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
