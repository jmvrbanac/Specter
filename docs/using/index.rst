.. -*- coding: utf-8 -*-

.. role:: raw-html(raw)
   :format: html

Using Specter
##################

Installation
=============
You can download Specter from PyPI for easy installation.
It is recommended that you use  `pip
<http://pypi.python.org/pypi/pip>`_ or `easy_install
<http://python-distribute.org/distribute_setup.py>`_ to install the bindings::

  pip install specter

You may consider using `virtualenv <http://www.virtualenv.org>`_ or `pyenv <https://github.com/yyuu/pyenv>`_ to create isolated Python environments.

Setup
==========
By default, Specter looks within the current directory for a folder called "spec" which contains your test files

*Example Default Test Structure:*

::

   Project_Folder
       └── spec
           ├── submodule
               ├── another.py
               └── __init__.py
           ├── example.py
           └── __init__.py

If you do not wish to use the default folder, you can specify an alternative using the :raw-html:`"--search"` command-line argument::

   specter --search /path/to/folder

Runner
==============
Specter allows for quick and easy execution of your tests by just calling 'specter' within your project folder::

	specter
	          ___
	        _/ @@\
	    ~- ( \  O/__     Specter
	    ~-  \    \__)   ~~~~~~~~~~
	    ~-  /     \     Keeping the Bogeyman away from your code!
	    ~- /      _\
	       ~~~~~~~~~

	ExampleSpec
	  ∟ this is a test spec


	------------------------
	------- Summary --------
	Pass            | 1
	Skip            | 0
	Fail            | 0
	Error           | 0
	Incomplete      | 0
	Test Total      | 1
	 - Expectations | 1

	------------------------

Command-line Arguments
------------------------
Specter is a spec-based testing library to help facilitate BDD in Python.

=====================  ============
Argument               Description
=====================  ============
-h, --help             Show console help
--search PATH          Specifies the search path for spec files
--no-art               Disables the ASCII art on the runner
--coverage             Enables coverage.py integration. Configure using .coveragerc
--select-module        Selects a module path to run. Ex: sample.TestClass
--select-tests         Selects tests to run by name. (Comma delimited list)
--select-by-metadata   Selects tests to run by specifying a list of key=value pairs
--xunit-results        Output xUnit XML results into a specified file
--json-results         Saves Specter JSON results into a specifed file
--no-color             Disables ASCII color codes
--ascii-only           Disables color and uses only ascii characters (useful for CI systems).
--parallel             Activates parallel testing mode
--num-processes        Specifies the number of processes to use under parallel mode (default: 6)
--show-all-expects     Displays all expectations for test cases
=====================  ============

Selecting Tests
================

Specter provides three ways to select a subset of tests at run time. They can
be combined: for example, ``--select-module`` narrows the search space and
``--select-by-metadata`` then filters within that module.

By module
---------

``--select-module`` accepts a dot-separated module path matching the class
hierarchy inside your ``spec/`` folder::

    specter --select-module spec.users.UserCreationSpec

You can also target a whole sub-package::

    specter --select-module spec.users

By test name
------------

``--select-tests`` accepts a comma-separated list of test method names
(without the class prefix). The match is exact::

    # Run a single test
    specter --select-tests it_creates_a_user

    # Run multiple tests
    specter --select-tests it_creates_a_user,it_deletes_a_user

By metadata
-----------

``--select-by-metadata`` accepts a space-separated list of ``key=value``
pairs. Only tests decorated with matching :func:`~specter.metadata` tags are
run::

    # Run only smoke tests
    specter --select-by-metadata type=smoke

    # Run tests tagged as both smoke and positive
    specter --select-by-metadata type=smoke kind=positive

Combining selectors
--------------------

All three selectors can be combined in a single invocation. The module filter
is applied first, then the name/metadata filters operate on the resulting set::

    specter --select-module spec.api \
            --select-by-metadata type=smoke \
            --xunit-results results/smoke.xml

Coverage
=========

Enable coverage tracking by passing ``--coverage``. Configure what to include
or exclude using a ``.coveragerc`` file in your project root.

*Minimal .coveragerc example:*

.. code-block:: ini

    [run]
    source = mypackage
    omit =
        spec/*
        */vendor/*

    [report]
    show_missing = True

Then run::

    specter --coverage

CI/CD Integration
==================

Specter integrates with CI pipelines through its xUnit XML output
(``--xunit-results``) and ``--ascii-only`` flag, which removes color codes
and Unicode symbols that can confuse log parsers.

GitHub Actions
--------------

.. code-block:: yaml

    name: Tests
    on: [push, pull_request]

    jobs:
      test:
        runs-on: ubuntu-latest
        strategy:
          matrix:
            python-version: ["3.10", "3.11", "3.12", "3.13"]

        steps:
          - uses: actions/checkout@v4

          - name: Set up Python ${{ matrix.python-version }}
            uses: actions/setup-python@v5
            with:
              python-version: ${{ matrix.python-version }}

          - name: Install dependencies
            run: pip install -e .[dev]

          - name: Run tests
            run: specter --ascii-only --xunit-results results/xunit.xml

          - name: Publish test results
            uses: EnricoMi/publish-unit-test-result-action@v2
            if: always()
            with:
              files: results/xunit.xml

GitLab CI
----------

.. code-block:: yaml

    test:
      image: python:3.12
      script:
        - pip install -e .[dev]
        - specter --ascii-only --xunit-results results/xunit.xml
      artifacts:
        when: always
        reports:
          junit: results/xunit.xml

Jenkins
-------

.. code-block:: groovy

    pipeline {
        agent any
        stages {
            stage('Test') {
                steps {
                    sh 'pip install -e .[dev]'
                    sh 'specter --ascii-only --xunit-results results/xunit.xml'
                }
                post {
                    always {
                        junit 'results/xunit.xml'
                    }
                }
            }
        }
    }

Running with coverage in CI
----------------------------

Add ``--coverage`` to any of the commands above and configure ``.coveragerc``
as shown in the Coverage section. The coverage report is printed to stdout at
the end of the run.
