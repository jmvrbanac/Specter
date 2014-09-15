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
