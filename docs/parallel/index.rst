.. -*- coding: utf-8 -*-

.. role:: raw-html(raw)
   :format: html

Parallel Testing in Specter
############################

For those who need their tests run in a parallel processes, Specter provides a parallel mode.
Parallel mode distributes all tests across multiple python processes. This is especially useful if you have a vast quantity of tests or many tests that take a long amount of time.

Usage
-------------

Activating parallel mode is simple::

    specter --parallel

.. note::
    Keep in mind that you can tune how many processes are spawned through the --num-processes argument. 


Differences using the parallel runner
-------------------------------------------------

Reporting
^^^^^^^^^^
One of the key differences you'll notice is that the reporting is entirely different. Due to the nature of the parallel testing, the normal
verbose/pretty Specter output is really not feasible. As a result, we currently provide a simple "dot" reporter with failed output in the pretty format. This allows for us to maintain a decent level of performance for users with very large numbers of tests. In the future, we plan on having specialty reporters for the parallel runner that provide more information.

.. note:: 
    The xUnit reporter is available in parallel mode as well.

State
^^^^^^^
Due to the concept of parallelism, sharing live state between tests through the class instance is very costly and quite impractical. As a result, Specter does not sync state between tests during test execution. However, each Spec provides before_all() and after_all() functions to which is called before and after test execution, so that state is carried into the tests.