.. -*- coding: utf-8 -*-

Migrating from pytest
######################

This guide is for developers who are familiar with pytest and want to
understand how Specter concepts map to what they already know.

Core Differences
=================

+--------------------+--------------------------------+----------------------------------+
| Concept            | pytest                         | Specter                          |
+====================+================================+==================================+
| Test suite         | Module / class                 | ``Spec`` subclass                |
+--------------------+--------------------------------+----------------------------------+
| Test case          | ``test_*`` function            | Any public method                |
+--------------------+--------------------------------+----------------------------------+
| Nested suites      | Not supported natively         | Nested ``Spec`` subclass         |
+--------------------+--------------------------------+----------------------------------+
| Setup (per suite)  | ``setup_class`` / fixture      | ``before_all`` / ``after_all``   |
+--------------------+--------------------------------+----------------------------------+
| Setup (per test)   | ``setup_method`` / fixture     | ``before_each`` / ``after_each`` |
+--------------------+--------------------------------+----------------------------------+
| Assertion          | ``assert`` statement           | ``expect(...).to.equal(...)``    |
+--------------------+--------------------------------+----------------------------------+
| Fatal assertion    | ``assert`` (always fatal)      | ``require(...).to.equal(...)``   |
+--------------------+--------------------------------+----------------------------------+
| Non-fatal assert   | ``pytest-check`` plugin        | ``expect(...)`` (default)        |
+--------------------+--------------------------------+----------------------------------+
| Skip               | ``@pytest.mark.skip``          | ``@skip(reason)``                |
+--------------------+--------------------------------+----------------------------------+
| Conditional skip   | ``@pytest.mark.skipif``        | ``@skip_if(condition)``          |
+--------------------+--------------------------------+----------------------------------+
| Parameterize       | ``@pytest.mark.parametrize``   | ``DataSpec``                     |
+--------------------+--------------------------------+----------------------------------+
| Shared fixtures    | ``@pytest.fixture``            | ``@fixture`` base class          |
+--------------------+--------------------------------+----------------------------------+
| Tagging / marking  | ``@pytest.mark.<name>``        | ``@metadata(key=value)``         |
+--------------------+--------------------------------+----------------------------------+

Example Comparison
==================

**pytest:**

.. code-block:: python

    import pytest

    class TestCalculator:
        def setup_method(self):
            self.calc = Calculator()

        def test_addition(self):
            assert self.calc.add(1, 2) == 3

        def test_raises(self):
            with pytest.raises(ZeroDivisionError):
                self.calc.divide(1, 0)

    @pytest.mark.parametrize('a,b,expected', [
        (1, 2, 3),
        (10, 20, 30),
    ])
    def test_add_parametrized(a, b, expected):
        assert Calculator().add(a, b) == expected


**Specter equivalent:**

.. code-block:: python

    from specter import Spec, DataSpec, expect

    class CalculatorSpec(Spec):
        def before_each(self):
            self.calc = Calculator()

        def it_adds_two_numbers(self):
            expect(self.calc.add(1, 2)).to.equal(3)

        def it_raises_on_divide_by_zero(self):
            expect(lambda: self.calc.divide(1, 0)).to.raise_a(ZeroDivisionError)

    class AdditionSpec(DataSpec):
        DATASET = {
            'small': {'a': 1, 'b': 2, 'expected': 3},
            'large': {'a': 10, 'b': 20, 'expected': 30},
        }

        def it_adds_correctly(self, a, b, expected):
            expect(Calculator().add(a, b)).to.equal(expected)


Key Behavioral Differences
============================

Non-fatal assertions
---------------------

The most significant behavioral difference is how assertion failures are
handled. In pytest, any ``assert`` failure immediately stops the test. In
Specter, ``expect()`` records the failure but lets the test continue. This
allows you to see all failures in a single test run.

Use ``require()`` when you want pytest-style immediate failure, for example
when a later assertion would error (not just fail) if an earlier value is
wrong::

    require(response).not_to.be_none()
    expect(response.status_code).to.equal(200)   # only runs if response is not None

Test naming
-----------

pytest requires test functions to be prefixed with ``test_``. Specter has no
such restriction: any public method (no leading underscore) on a ``Spec`` is
a test. This means names like ``it_creates_a_user`` or
``when_the_database_is_empty`` are perfectly valid.

Test discovery
--------------

pytest discovers files matching ``test_*.py`` or ``*_test.py``. Specter
discovers all Python files inside the ``spec/`` directory (or whichever path
you pass to ``--search``).

Fixtures vs. fixture decorator
--------------------------------

pytest fixtures are functions decorated with ``@pytest.fixture`` and injected
via parameter names. Specter fixtures are base classes decorated with
``@fixture``. They are not executed directly as tests but provide shared
tests and lifecycle hooks to every class that inherits them.

.. code-block:: python

    from specter import Spec, fixture, expect

    @fixture
    class DatabaseFixture(Spec):
        def before_each(self):
            self.db = connect_to_test_db()

        def after_each(self):
            self.db.close()

    class UserRepoSpec(DatabaseFixture):
        def it_creates_a_user(self):
            user = self.db.users.create(name='Alice')
            expect(user.id).not_to.be_none()

Running Selected Tests
-----------------------

+-------------------------------------+-----------------------------------------------+
| Task                                | Command                                       |
+=====================================+===============================================+
| Run all tests                       | ``specter``                                   |
+-------------------------------------+-----------------------------------------------+
| Run a specific module               | ``specter --select-module spec.users``        |
+-------------------------------------+-----------------------------------------------+
| Run tests by name                   | ``specter --select-tests it_creates_a_user``  |
+-------------------------------------+-----------------------------------------------+
| Run tests by tag                    | ``specter --select-by-metadata type=smoke``   |
+-------------------------------------+-----------------------------------------------+
| Run with keyword (pytest -k equiv)  | ``specter --select-tests name1,name2``        |
+-------------------------------------+-----------------------------------------------+
