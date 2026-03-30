.. -*- coding: utf-8 -*-

Troubleshooting
################

This page covers common pitfalls and unexpected behaviors you may encounter
when using Specter.

``self`` is not an instance of my Spec class
============================================

**Symptom:** Accessing an attribute set on ``self`` inside ``before_all``
fails in ``before_each``, or calling ``super()`` raises a ``TypeError``.

**Cause:** Specter executes each test suite under a *state object* that
mirrors your class hierarchy but is not literally an instance of your
``Spec`` subclass. This is intentional: it prevents test-level attributes
from accidentally conflicting with Specter's own infrastructure.

**Calling super() from lifecycle hooks:**

.. code-block:: python

    from specter import Spec

    class BaseSpec(Spec):
        def before_each(self):
            self.client = create_client()

    class MySpec(BaseSpec):
        def before_each(self):
            # self is the state object, not MySpec, so you must use type(self)
            super(type(self), self).before_each()
            self.extra = 'value'

**See also:** :ref:`test-state`

Tests in ``before_all`` / ``after_all`` don't see each other's state
======================================================================

**Symptom:** A value set on ``self`` inside ``before_all`` is not visible
in ``after_all``, or vice versa.

**Cause:** The same state object issue as above. The state object is shared
within a single suite execution, so attributes set in ``before_all`` *are*
visible in test methods and ``after_all``. If you're not seeing them, double
check that you're assigning to ``self`` (the state object) and not to a
local variable.

Parallel mode: state set in one test is not visible in another
==============================================================

**Symptom:** A value stored on ``self`` in one test is not available in
another test when running with ``--parallel``.

**Cause:** This is by design. Parallel mode distributes tests across multiple
processes. Shared in-memory state between processes is not feasible without
explicit inter-process communication. Set up any shared state in
``before_all``, which runs in each process before its batch of tests.

Tests are not discovered
=========================

**Symptom:** ``specter`` runs but reports 0 tests.

**Checklist:**

1. Make sure your test files are inside the ``spec/`` directory (or the path
   you passed to ``--search``).
2. Make sure each directory in the ``spec/`` tree contains an ``__init__.py``
   file so Python can import them.
3. Check that your test class inherits from ``Spec`` or ``DataSpec`` and is
   not decorated with ``@fixture``.
4. Check that your test methods do not start with ``_`` and are not named
   ``execute``, ``serialize``, ``before_each``, ``after_each``,
   ``before_all``, or ``after_all``.

A test passes even though an expect failed
==========================================

**Symptom:** The console shows a failing expectation, but the test is marked
as passing.

**Cause:** ``expect()`` failures are non-fatal: they are recorded against the
test case but do not raise an exception. A test case is only marked as
*failed* if at least one ``expect`` failed, or if an unhandled exception
occurred. If you believe the test should stop on failure, use ``require()``
instead.

``require()`` stops the test -- subsequent expects don't run
=============================================================

This is intentional. ``require()`` is a fatal assertion: as soon as it fails,
a ``FailedRequireException`` is raised internally and the test stops. Use
``require()`` only for preconditions where running the rest of the test would
be meaningless or produce misleading errors.

Coverage is not reporting the right files
==========================================

Configure ``.coveragerc`` to match your project layout. A minimal example::

    [run]
    source = mypackage
    omit =
        spec/*
        */vendor/*

Then run::

    specter --coverage

xUnit output file is not created
=================================

Make sure you pass the *path* to the output file, not just a flag::

    specter --xunit-results results/xunit.xml

If the directory does not exist, create it first. Specter will not create
parent directories automatically.

Unicode characters appear garbled in CI output
===============================================

Use ``--ascii-only`` to disable Unicode characters and color codes. This
replaces symbols like ``∟`` with plain ASCII equivalents and is safe for
environments that do not support UTF-8::

    specter --ascii-only
