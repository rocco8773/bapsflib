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
from sphinx.ext.autodoc import between
# from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath('..'))

# autodoc_mock_imports = ['PyQt5']
autoclass_content = "both"

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# 'sphinx.ext.imgmath'
# 'sphinx.ext.mathjax'
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.githubpages',
              'sphinx.ext.mathjax',
              'sphinx.ext.autosummary']
numfig = True  # enable figure and table numbering
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'bapsflib'
copyright = '2017-2018, Erik T. Everson'
author = 'Erik T. Everson'

# The version info for the project you're documenting, acts as
# replacement for |version| and |release|, also used in various other
# places throughout the built documents.
#
# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''

# The language for content autogenerated by Sphinx. Refer to
# documentation for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce
# nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation
# for a list of builtin themes.
#
#html_theme = 'alabaster'
#html_theme = 'default'
#on_rtd = os.environ.get('READTHEDOCS') == 'True'
#if on_rtd:
#    html_theme = 'default'
#else:
#    html_theme = 'sphinx_rtd_theme'
html_theme = 'sphinx_rtd_theme'
#html_theme_path = ['_themes']

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see
# the documentation.
#
html_theme_options = {
    'navigation_depth': 8,  # depth of readthedocs sidebar
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
html_static_path = ['_static']
# html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document
# names to template names.
#
# This is required for the alabaster theme
# refs:
#  http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'bapsflibdocs'


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
    (master_doc, 'bapsflib.tex', 'bapsflib Documentation',
     'Erik T. Everson', 'manual'),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'bapsflib', 'bapsflib Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'bapsflib', 'bapsflib Documentation',
     author, 'bapsflib', 'One line description of project.',
     'Miscellaneous'), ]

# -- My Added Extras ---------------------------------------------------

# A list of prefixes that are ignored for sorting the Python module
# index (e.g., if this is set to ['foo.'], then foo.bar is shown under
# B, not F).
modindex_common_prefix = ['bapsflib.']

# prevents files that match these patterns from being included in source
# files
# - prevents file file.inc.rst from being loaded twice: once when
#   included as a source file and second when it's inserted into another
#   .rst file with .. include
#
exclude_patterns.extend([
    '**.inc.rst'
])

# add a pycode role for inline markup e.g. :pycode:`'mycode'`
rst_prolog = """
.. role:: pycode(code)
   :language: python3

.. role:: red

.. role:: ibf
    :class: ibf
"""


def setup(app):
    # Register a sphinx.ext.autodoc.between listener to ignore
    # everything between lines that contain the word IGNORE
    #
    # Usage:
    #    """
    #    IGNORE:
    #        everything here is ignored
    #    IGNORE
    #    """
    app.connect('autodoc-process-docstring', between('^.*IGNORE.*$',
                                                     exclude=True))

    # prevent horizontal scrolling in readthedoc themed tables
    app.add_stylesheet('rtd_theme_overrides.css')
    return app


#class Mock(MagicMock):
#    @classmethod
#    def __getattr__(cls, name):
#            return MagicMock()
#
#MOCK_MODULES = ['PyQt5', 'PyQt5.uic', 'numpy', 'pandas', 'h5py',
#                'viewers']
#sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
