.. role:: raw-html(raw)
   :format: html

Release Notes
=================

Release: 0.2.0 (not released)
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Switching to only showing error/failed expectations by default.
    The old style of showing all expectations is still available through
    the --show-all-expects cli argument - gh-#46
 #. Fixing the summary report colors to reflect the actual test results. - gh-#44
 #. Added the ability for reporters to add their own cli arguments
 #. Breaking reporter contract by switching from subscribe_to_describe(self, describe)
    to subscribe_to_spec(self, spec). This is due to the slow removal of the
    "describe" terminology in Specter.


Release: 0.1.15
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixing PyPI package number - gh-#43


Release: 0.1.14
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixed Coverage.py integration - gh-#36 gh-#40
 #. Fixed coverage reporting in parallel mode - gh-#40
 #. Fixed duplicated traceback information on errors - gh-#42
 #. Fixed difficult to trace error messages with expected parameters - gh-#41
 #. Added support for execution of specter through Coverage (i.e. coverage run -m specter)


Release: 0.1.13
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Added clean test state per suite - gh-#37 gh-#13
 #. Added basic parallel testing - gh-#3
 #. Fixed xUnit test class path
 #. Fixed standard reporter to not be red all the time - gh-#28
 #. Fixed be_in() assertion - gh-#34
 #. Fixed metadata decorator not re-raising assertions - gh-#35


Release: 0.1.12
----------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixing packaging issue where it wasn't including the specter.reporting package.


Release: 0.1.11
----------------

Special thanks to `John Wood <https://github.com/jfwood>`_ for his contributions to this release!

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixed Jenkins unicode error - gh-#27
 #. Refactored reporting system to be plugin centric - gh-#21
 #. Added no-color mode for CI systems - gh-#19
 #. Added xUnit output reporter - gh-#10
 #. Added duplication filter on data-driven dataset items - gh-#6
 #. Added console output of parameters on a failed data-driven test - gh-#2
 #. Added error line indicator on tracebacks
 #. Added checks and x's as pass/fail indicators
