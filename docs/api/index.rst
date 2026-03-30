.. -*- coding: utf-8 -*-

API Reference
##############

This page documents the public API that you import from ``specter``.

Test Suite Classes
==================

.. autoclass:: specter.Spec
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: specter.DataSpec
   :members:
   :show-inheritance:

Fixtures
--------

.. autofunction:: specter.fixture

Assertions
==========

.. autofunction:: specter.expect

.. autofunction:: specter.require

.. autoclass:: specter.expect.ExpectAssert
   :members: equal, almost_equal, be_greater_than, be_less_than, be_none,
             be_true, be_false, contain, be_in, be_a, be_an_instance_of,
             raise_a

Test Decorators
===============

.. autofunction:: specter.skip

.. autofunction:: specter.skip_if

.. autofunction:: specter.incomplete

.. autofunction:: specter.metadata

Custom Reporters
================

.. autoclass:: specter.reporting.AbstractReporterPlugin
   :members:

.. autoclass:: specter.reporting.AbstractSerialReporter
   :members:
   :show-inheritance:

.. autoclass:: specter.reporting.AbstractParallelReporter
   :members:
   :show-inheritance:

.. autoclass:: specter.reporting.AbstractConsoleReporter
   :members:
   :show-inheritance:

Events
------

.. autoclass:: specter.spec.DescribeEvent
   :members:

.. autoclass:: specter.spec.TestEvent
   :members:
