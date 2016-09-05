.. role:: raw-html(raw)
   :format: html

Release Notes
=================

Release: 0.5.1
--------------------------------

Special thanks to `Mark Church <https://github.com/GrandPubba>`_ for
his contribution to this release!

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Switching to bumpversion
 #. Fixing xunit reporting output issue - gh-#83

Release: 0.5.0
--------------------------------

Special thanks to `Alexander Shchapov <https://github.com/alexanderad>`_ for
his contribution to this release!

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Adding support for the almost_equal() expectation.
 #. Fixing issue where expect messages weren't getting captured across
    lines - gh-#47
 #. Fixing issue with --select-tests where it didn't properly select the
    the correct tests - gh-#69

Release: 0.4.2
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixing regression in raises_a expectation - gh-#67
 #. Adding support for the --ascii-only cli argument - gh-#68

Release: 0.4.1
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixing incorrect cli documentation for --select-module

Release: 0.4.0
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Adding support to execute individual tests - gh-#65
 #. Fixing issues with using a negative raises_a conditional - gh-#63

Release: 0.3.0
--------------------------------

Special thanks to `Paul Glass <https://github.com/pglass>`_ and
`Stas Sușcov <https://github.com/stas>`_ for their contributions to this
release!

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Switched to Pike for module loading and searching
 #. Added support for teardown hooks - gh-#61
 #. Fixed showing exceptions from old-style classes - gh-#57
 #. Support dataset values to contain lists of dicts - gh-#56

Release: 0.2.1
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Fixed --num-processes error - gh-#52
 #. Added extra error handling around except() - gh-#51
 #. Added Python 3.4 job to CI


Release: 0.2.0
--------------------------------

Features and bug fixes
^^^^^^^^^^^^^^^^^^^^^^^^

 #. Switching to only showing error/failed expectations by default.
    The old style of showing all expectations is still available through
    the --show-all-expects cli argument - gh-#46
 #. Adding support for the Specter report JSON format - gh-#12
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
