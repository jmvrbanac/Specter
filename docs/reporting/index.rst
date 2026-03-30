Reporting
##################

Types of reporting
===================

What is a reporter? A Specter reporter is a module that interacts with
test and spec events to produce human or machine-readable output. Currently,
Specter supports four types of reporters out of the box:

 * Console - Serial BDD-style output.
 * Dots - Parallel output that displays a dot per test.
 * xUnit - Produces xUnit compatible XML for CI tools.
 * Specter - Produces JSON in the Specter format for storage and CI tools.


Console
========

This the default reporter that is used when tests are run serially. It
gives a familiar BDD-style output for the user.

**Example Output**::

    SSH Client Verification
      ∟ can create an instance
      ∟ can connect
      ∟ sets key policy on client
      ∟ can close
      ∟ can execute a command
      ∟ can connect with args
      ∟ unassigned client auto creates a paramiko client

    ------------------------
    ------- Summary --------
    Pass            | 7
    Skip            | 0
    Fail            | 0
    Error           | 0
    Incomplete      | 0
    Test Total      | 7
     - Expectations | 14
    ------------------------



Dots
=====

This is the default reporter that is used when tests are run in parallel mode.
Due to the nature of parallel execution, it is impossible to build a BDD-style
report in real-time. As a result, Specter defaults to a simple dot-based report.
A single dot represents a passed test; whereas a failed test is marked with an
"x".

**Example Output**::

    .......xx.x
    11 Test(s) Executed!



Specter Format
====================

The specter format is designed to be a format that allows for you to easily
store and retrieve information about your tests. Considering this format is
just an expected structure around JSON, this format is especially useful
when combining with a document store such as MongoDB.


Root:
---------

=========== ===================================================================
Attribute   Note
=========== ===================================================================
format      Just a helper for parsers. It be the value "specter"
version     Aid for parsers to know what version of the format we are running.
specs       A list of spec objects that contain all of the test information
=========== ===================================================================

**Example:**

.. code-block:: javascript

    {
        "format": "specter",
        "version": "0.1.0",
        "specs": [...]
    }


Spec:
---------

\*attributes in *italics* are optional

=========== ===================================================================
Attribute   Note
=========== ===================================================================
id          The UUID generated during the test-run for the Spec
name        This is considered the "human-readable" name
class_path  The full qualified class path for the Spec
*doc*       Docstring associated with the Spec
cases       List of test case objects attached to the Spec
specs       List of child spec objects attached to the Spec
=========== ===================================================================

**Example:**

.. code-block:: javascript

    {
        "id": "35e9900f-9325-4e78-928d-593044c1a4f0",
        "name": "Key Based",
        "class_path": "spec.rift.clients.ssh.SSHCredentials.KeyBased",
        "doc": null,
        "cases": [...],
        "specs": [...]
    }


Case:
---------

\*attributes in *italics* are optional

================ =============================================================================
Attribute        Note
================ =============================================================================
id               The UUID generated during the test-run for the Case
name             This is consider the "human-readable" name
raw_name         The actual test name
start            The exact time when the test started (expressed in seconds since the epoch)
end              The exact time when the test ended (expressed in seconds since the epoch)
skipped          Boolean to indicate if the test was skipped for some reason
metadata         Dictionary containing the metadata that was attached to the test case
expects          List of expectation / requirement objects executed on the test
success          Is true when all expects successfully pass without errors or failures
*skip_reason*    String specifying the reason for why the test was skipped
*doc*            Docstring associated with the test case
*error*          Contains the error traceback associated with a test
*execute_kwargs* During Data-Driven tests, this contains the kwargs used during execution
================ =============================================================================

**Example:**

.. code-block:: javascript

    {
        "id": "1aa40954-d207-4264-a80f-e05605f57bd3",
        "name": "can generate a paramiko key",
        "raw_name": "can_generate_a_paramiko_key",
        "start": 1410748788.813371,
        "end": 1410748788.81438,
        "success": true,
        "skipped": false,
        "metadata": {},
        "expects": [...]
    }


Expect:
---------

=========== ===================================================================
Attribute   Note
=========== ===================================================================
assertion   The stringified version of the test assertion
required    Indicates if the expectation was a requirement i.e. require(...)
success     Indicates the pass/fail status of the expecation
=========== ===================================================================

**Example:**

.. code-block:: javascript

    {
        "assertion": "sample to equal [1]",
        "required": false,
        "success": true
    }


Custom Reporters
================

Specter discovers reporter plugins automatically from within the
``specter.reporting`` package. You can write your own reporter by subclassing
one of the abstract base classes and placing it in a package that Specter
can discover, or by contributing it to the ``specter/reporting/`` directory
directly.

Choosing a base class
----------------------

+-------------------------------+-------------------------------------------+
| Base class                    | Use when                                  |
+===============================+===========================================+
| ``AbstractSerialReporter``    | Standard (non-parallel) test runs         |
+-------------------------------+-------------------------------------------+
| ``AbstractParallelReporter``  | Parallel test runs (``--parallel``)       |
+-------------------------------+-------------------------------------------+
| ``AbstractConsoleReporter``   | Reporters that write a summary to stdout  |
+-------------------------------+-------------------------------------------+

You can inherit from multiple base classes if your reporter should work in
both serial and parallel modes.

Events
-------

Reporters react to events by subscribing listeners in ``subscribe_to_spec``.
Two event types are available:

``DescribeEvent``
    Fired when a suite (``Spec``) starts or finishes.

    * ``DescribeEvent.START`` -- payload is the ``Describe`` instance.
    * ``DescribeEvent.COMPLETE`` -- payload is the ``Describe`` instance.

``TestEvent``
    Fired when a single test case finishes.

    * ``TestEvent.COMPLETE`` -- payload is the ``CaseWrapper`` instance.

The ``CaseWrapper`` payload exposes:

* ``pretty_name`` -- human-readable test name.
* ``success`` -- bool, True if all expectations passed.
* ``skipped`` / ``skip_reason`` -- skip status and reason string.
* ``incomplete`` -- bool, True if the test is marked ``@incomplete``.
* ``error`` -- list of traceback lines, or ``None``.
* ``expects`` -- list of ``ExpectAssert`` objects, each with a ``success``
  flag and ``assertion`` string.
* ``elapsed_time`` -- float, seconds the test took.
* ``metadata`` -- dict of key/value pairs from the ``@metadata`` decorator.

Implementing a reporter
------------------------

.. code-block:: python

    from specter.spec import TestEvent, DescribeEvent
    from specter.reporting import AbstractSerialReporter, AbstractConsoleReporter


    class MyReporter(AbstractConsoleReporter, AbstractSerialReporter):

        def get_name(self):
            return 'My Custom Reporter'

        def add_arguments(self, argparser):
            """Add any custom CLI arguments here."""
            argparser.add_argument(
                '--my-output', dest='my_output', default=None,
                help='Path to write custom output')

        def process_arguments(self, args):
            """Read parsed arguments here."""
            self.output_path = getattr(args, 'my_output', None)

        def subscribe_to_spec(self, spec):
            spec.add_listener(DescribeEvent.START, self.on_suite_start)
            spec.add_listener(TestEvent.COMPLETE, self.on_test_complete)

        def on_suite_start(self, evt):
            suite = evt.payload
            print(f'Suite: {suite.name}')

        def on_test_complete(self, evt):
            case = evt.payload
            status = 'PASS' if case.success else 'FAIL'
            print(f'  [{status}] {case.pretty_name}')

        def print_summary(self):
            print('Done.')

        def finished(self):
            if self.output_path:
                with open(self.output_path, 'w') as f:
                    f.write('custom output here')

.. note::
    Specter discovers reporters by scanning the ``specter.reporting`` module
    for subclasses of ``AbstractReporterPlugin``. If you want Specter to pick
    up your reporter automatically you need to place it inside that package.
    The cleanest approach for external reporters is to place your reporter
    module inside ``specter/reporting/`` in your own fork or contrib package.
