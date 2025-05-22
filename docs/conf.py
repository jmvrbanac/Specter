import sys
import os
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../'))

# -- General configuration --

extensions = ['sphinx.ext.autodoc']

# Issue tracking
issuetracker = 'github'
issuetracker_project = 'jmvrbanac/Specter'
issuetracker_issue_pattern = r'gh-#(\d+)'
# issuetracker_title_template = '#{issue.id}'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['doc_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Specter'
copyright = u'2013-2017, John Vrbanac'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

version = '0.7.0'
release = '0.7.0'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['doc_build']

pygments_style = 'friendly'


# -- Options for HTML output --

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True
htmlhelp_basename = 'Specterdoc'


# -- Options for LaTeX output --

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',
    'classoptions': ',oneside',
    'babel': '\\usepackage[english]{babel}',
    'inputenc': '',
    'utf8extra': '',
    'fontenc': '',
    'preamble': ''''''
}

latex_documents = [
    ('index', 'Specter.tex', u'Specter Documentation',
     u'John Vrbanac', 'manual'),
]


# -- Options for manual page output --

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'specter', u'Specter Documentation',
     [u'John Vrbanac'], 1)
]


# -- Options for Texinfo output --

texinfo_documents = [
    ('index', 'Specter', u'Specter Documentation', u'John Vrbanac', 'Specter',
     'One line description of project.', 'Miscellaneous'),
]
