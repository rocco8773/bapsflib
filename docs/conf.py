#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# bapsflib documentation build configuration file, created by
# sphinx-quickstart on Mon Aug 21 21:16:40 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import os
import sys

from datetime import datetime
from packaging.version import Version
from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath(".."))

from bapsflib import __version__ as release

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "hoverxref.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "sphinx_changelog",
]

# Setup intersphinx
intersphinx_mapping = {
    "astropy": ("http://docs.astropy.org/en/stable/", None),
    "h5py": ("https://docs.h5py.org/en/latest/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "numpydoc": ("https://numpydoc.readthedocs.io/en/latest/", None),
    "plasmapy": ("https://docs.plasmapy.org/en/latest/", None),
    "python": ("https://docs.python.org/3", None),
    "readthedocs": ("https://docs.readthedocs.io/en/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "sphinx_automodapi": (
        "https://sphinx-automodapi.readthedocs.io/en/latest/",
        None,
    ),
}

# Setup hoverxref
hoverxref_intersphinx = list(intersphinx_mapping.keys())
hoverxref_auto_ref = True
hoverxref_domains = ["py"]  # ["py", "cite"]
hoverxref_mathjax = True
hoverxref_roles = ["confval", "term"]
hoverxref_sphinxtabs = True
hoverxref_tooltip_maxwidth = 600  # RTD main window is 696px
hoverxref_role_types = {
    # roles with cite domain
    # "p": "tooltip",
    # "t": "tooltip",
    # roles with py domain
    "attr": "tooltip",
    "class": "tooltip",
    "const": "tooltip",
    "data": "tooltip",
    "exc": "tooltip",
    "func": "tooltip",
    "meth": "tooltip",
    "mod": "tooltip",
    "obj": "tooltip",
    # roles with std domain
    "confval": "tooltip",
    "hoverxref": "tooltip",
    "ref": "tooltip",
    "term": "tooltip",
}

if building_on_readthedocs := os.environ.get("READTHEDOCS"):
    # Using the proxied API endpoint is a Read the Docs strategy to
    # avoid a cross-site request forgery block for docs using a custom
    # domain. See conf.py for sphinx-hoverxref.
    use_proxied_api_endpoint = os.environ.get("PROXIED_API_ENDPOINT")
    hoverxref_api_host = "/_" if use_proxied_api_endpoint else "https://readthedocs.org"

# Various sphinx configuration variables
autoclass_content = "both"  # for classes insert docstrings from __init__ and class
numfig = True  # enable figure and table numbering
autosummary_generate = True  # generate stub files from all found autosummary directives
default_role = "py:obj"  # default role for reST role (i.e. `` defaults to :py:obj:``)

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "bapsflib"
author = "Erik T. Everson & the BaPSF Community"
copyright = f"2017-{datetime.utcnow().year}, {author}"

# The version info for the project you're documenting, acts as
# replacement for |version| and |release|, also used in various other
# places throughout the built documents.
#
# The full version, including alpha/beta/rc tags.
#  Note: If plasmapy.__version__ can not be defined then it is set to 'unknown'.
#        However, release needs to be a semantic style version number, so set
#        the 'unknown' case to ''.
release = "" if release == "unknown" else release
revision = ""
if release != "":
    pv = Version(release)
    release = pv.public
    revision = "" if pv.local is None else pv.local[1:]
version = ".".join(release.split(".")[:2])  # short X.Y version

# The language for content autogenerated by Sphinx. Refer to
# documentation for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce
# nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation
# for a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see
# the documentation.
#
html_logo = "./_static/BaPSF_Logo_White_RGB_150px.png"
html_favicon = "./_static/BaPSF_Logo_Color_white_background_RGB_32px.ico"
html_theme_options = {
    "navigation_depth": 8,  # depth of readthedocs sidebar
    "logo_only": False,
}

# Add any paths that contain custom static files (such as style sheets)
# here, relative to this directory. They are copied after the builtin
# static files, so a file named "default.css" will overwrite the builtin
# "default.css".
# - attempt to solve RTD from throwing a WARNING: html_static_theme
#   entry ... does not exist
# - see issue #1776 on rtfd/readthedocs.org
#   (https://github.com/rtfd/readthedocs.org/issues/1776)
#
html_static_path = ["_static"]
# html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document
# names to template names.
#
# This is required for the alabaster theme
# refs:
#  http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
        "donate.html",
    ]
}


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "bapsflibdocs"


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "bapsflib.tex", "bapsflib Documentation", "Erik T. Everson", "manual"),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "bapsflib", "bapsflib Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "bapsflib",
        "bapsflib Documentation",
        author,
        "bapsflib",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# -- My Added Extras ---------------------------------------------------

# A list of prefixes that are ignored for sorting the Python module
# index (e.g., if this is set to ['foo.'], then foo.bar is shown under
# B, not F).
modindex_common_prefix = ["bapsflib."]

# prevents files that match these patterns from being included in source
# files
# - prevents file file.inc.rst from being loaded twice: once when
#   included as a source file and second when it's inserted into another
#   .rst file with .. include
#
exclude_patterns.extend(["**.inc.rst"])

# add a pycode role for inline markup e.g. :pycode:`'mycode'`
rst_prolog = """
.. role:: pycode(code)
   :language: python3

.. role:: red
.. role:: green
.. role:: blue

.. role:: ibf
    :class: ibf

.. role:: textit
    :class: textit

.. role:: textbf
    :class: textbf
"""


def setup(app: Sphinx) -> None:
    # custom config values
    app.add_config_value("revision", "", True)

    # custom CSS overrides
    app.add_css_file("rtd_theme_overrides.css")
