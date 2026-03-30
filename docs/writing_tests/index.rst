.. -*- coding: utf-8 -*-

.. role:: raw-html(raw)
   :format: html

Writing Specter Tests
######################

Naming Rules
~~~~~~~~~~~~~~~~~
Most frameworks require you to start your test with a given prefix such as :raw-html:`"test_"`. Specter does not impose any prefix rules on test functions. We believe that it is better to give the developer more flexibility in naming so that their test names better describe what they are actually testing. However, Specter does have a few rules that should be followed.

* All helper functions should start with an underscore (_). Just as Python treats a single underscore as "protected", so does Specter.
* "before_each", "after_each", "before_all", and "after_all" are reserved for setup functions on your test suites (Specs).
* Currently, we also treat "serialize" and "execute" as reserved names as well.


Writing Tests
~~~~~~~~~~~~~~
Writing a test in Specter is simple.

1. Create a class which extends Spec
2. Create a function in that class that calls expect or require once

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter import Spec, expect

    class SampleSpec(Spec):
        """Docstring describing the specification"""
        def it_can_create_an_object(self):
            """ Test docstring"""
            expect('something').to.equal('something')

Test Setup / Teardown
~~~~~~~~~~~~~~~~~~~~~~
:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter import Spec, expect

    class SampleSpec(Spec):
        """Docstring describing the specification"""

        # Called once before any tests or child Specs are called
        def before_all(self):
            pass

        # Called after all tests and child Specs have been called
        def after_all(self):
            pass

        # Called before each test
        def before_each(self):
            pass

        # Called after each test
        def after_each(self):
            pass

        def it_can_create_an_object(self):
            """ Test docstring"""
            expect('something').to.equal('something')


Nested Tests
~~~~~~~~~~~~~~
Specter tests utilizes the concept of nested test suites. This allows for you to provide a clearer picture of what you are testing within your test suites. For those who have used Jasmine or RSpec should be relatively familiar with this concept from their implementation of Spec.

Within Specter you can create a nested test description (suite) in the form of a class that inherits from the Spec class.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter import Spec, expect

    class SampleSpec(Spec):

        class OtherFunctionalityOfSample(Spec):
            """ Docstring goes here """

            def it_should_do_something(self):
                """ Test Docstring """
                expect('trace').to.equal('trace')


Test Fixtures
~~~~~~~~~~~~~~
In Specter, a test fixture is defined as a test base class that is not treated as a runnable test specification. This allows for you to build reusable test suites through inheritance. To facilitate this, there is a decorator named "fixture" available in the spec module.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter import Spec, fixture, expect

    @fixture
    class ExampleTestFixture(Spec):

        def _random_helper_func(self):
            pass

        def sample_test(self):
            """This test will be on every Spec that inherits this fixture"""
            expect('something').to.equal('something')


    class UsingFixture(ExampleTestFixture):

        def another_test(self):
            expect('this').not_to.equal('that')

:raw-html:`<i>Expected Output (using --show-all-expects):</i>`

.. code-block:: bash

    UsingFixture
      ∟ sample test
        ✔ 'something' to equal 'something'
      ∟ another test
        ✔ 'this' not to equal 'that'


.. _test-state:

Test State and Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each test spec executes its tests under a clean state that does not contain
the attributes of the actual Spec class. This allows for users to not worry
about conflicting with the Specter infrastructure. However, the drawback to
this is that the instance of "self" within a test is not actually an instance
of the type defined in your hardcoded tests. This makes calling super a little
bit unconventional as you can see in the example below.

.. code-block:: python

    from specter import Spec

    class FirstSpec(Spec):
        def before_all(self):
            # Do something
            pass

    class SecondSpec(FirstSpec):
        def before_all(self):
            # self is actually an instance of the state object and not an instance of SecondSpec
            super(type(self), self).before_all()

            # Do something else

As you can see in the example, you still can inherit the attributes of your
other spec classes. However, you just have to keep in mind, that "self" is
actually the state object and not the actual instance of the spec.


Assertions / Expectations
~~~~~~~~~~~~~~~~~~~~~~~~~~
Assertions or expectations in Specter attempt to be as expressive as possible.
An expectation does **not** fast-fail the test -- execution continues even if
the expectation fails, and all failures are reported together.

Expectations follow this flow::

    expect(target).to.<comparison>(expected)
    expect(target).not_to.<comparison>(expected)

For example::

    expect(request.status_code).to.equal(200)
    expect(error_message).not_to.be_none()

Available Comparisons
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Comparison
     - Description
   * - ``equal(expected)``
     - Target ``==`` expected (strict equality).
   * - ``almost_equal(expected, places=7)``
     - Passes when ``round(abs(target - expected), places) == 0``.
       Use for floating-point comparisons.
   * - ``be_greater_than(expected)``
     - Target ``>`` expected.
   * - ``be_less_than(expected)``
     - Target ``<`` expected.
   * - ``be_none()``
     - Target ``is None``.
   * - ``be_true()``
     - Target is truthy.
   * - ``be_false()``
     - Target is falsy.
   * - ``be_a(type)``
     - ``type(target) is type`` -- exact type match, no subclasses.
   * - ``be_an_instance_of(type)``
     - ``isinstance(target, type)`` -- passes for subclasses.
   * - ``be_in(collection)``
     - Target is a member of *collection*.
   * - ``contain(item)``
     - *collection* target contains *item*.
   * - ``raise_a(exception_type)``
     - Target callable raises the given exception type.

Negating an assertion
-----------------------

Any comparison can be negated by using ``.not_to`` instead of ``.to``:

.. code-block:: python

    expect('hello').not_to.equal('world')
    expect(result).not_to.be_none()
    expect([]).not_to.contain('item')
    expect(some_func).not_to.raise_a(ValueError)

Asserting a raised exception
-----------------------------

Pass the callable and its arguments separately to ``expect``:

.. code-block:: python

    def divide(a, b):
        return a / b

    # No arguments
    expect(lambda: divide(1, 0)).to.raise_a(ZeroDivisionError)

    # With arguments via caller_args list
    expect(divide, [1, 0]).to.raise_a(ZeroDivisionError)

    # Assert it does NOT raise
    expect(divide, [10, 2]).not_to.raise_a(ZeroDivisionError)

Floating-point comparisons
---------------------------

Use ``almost_equal`` when comparing floats to avoid precision issues:

.. code-block:: python

    expect(0.1 + 0.2).to.almost_equal(0.3, places=5)

Fast-fail expectations
^^^^^^^^^^^^^^^^^^^^^^^
In some cases you need to stop the test immediately upon failure. With Specter,
we call these requirements. Use ``require`` when subsequent assertions only
make sense if an earlier one passes.

.. code-block:: python

    from specter import Spec, expect, require

    class ApiSpec(Spec):
        def it_returns_valid_json(self):
            response = get('/api/users/1')
            require(response.status_code).to.equal(200)
            # The lines below only run if the status code check passed
            require(response.json()).not_to.be_none()
            expect(response.json()['id']).to.be_a(int)

If the status code is not 200, the test stops immediately. This prevents
misleading errors from cascading through assertions that depend on earlier
ones being true.


Data-Driven Tests
~~~~~~~~~~~~~~~~~~
Often times you find that you need to run numerous types of data through a given test case. Rather than having to duplicate your tests a large number of times, you can utilize the concept of Data-Driven Tests. This will allow for you to subject your test cases to specified dataset.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter import DataSpec

    class ExampleData(DataSpec):
        DATASET = {
            'test': {'data_val': 'sample_text'},
            'second_test': {'data_val': 'sample_text2'}
        }

        def sample_data(self, data_val):
            expect(data_val).to.equal('sample_text')

This dataset will produce a Spec with two tests: "sample_data_test" and "sample_data_second_test" each passed in "sample_text" under the data_val parameter.

:raw-html:`<i>This would produce a console output similar to (using --show-all-expects):</i>`

.. code-block:: bash

    Example Data
      ∟ sample data test
        ✔ "sample_text" to equal "sample_text"
      ∟ sample data second test
        ✘ "sample_text2" to equal "sample_text"


Metadata in Data-Driven
^^^^^^^^^^^^^^^^^^^^^^^^^
There are two different methods of adding metadata to your data-driven tests. The first method is to assign metadata to the entire set of data-driven tests.

.. code-block:: python

    from specter import DataSpec

    class ExampleData(DataSpec):
        DATASET = {
            'test': {'data_val': 'sample_text'},
            'second_test': {'data_val': 'sample_text'}
        }

        @metadata(test='smoke')
        def sample_data(self, data_val):
            expect(data_val).to.equal('sample_text')

This will assign the metadata attributes to all tests that are generated from the decoratored instance method.
The second way of assigning metadata is by creating a more complex dataset item. A complex dataset item contains two keys; args and meta.

.. code-block:: python

    from specter import DataSpec

    class ExampleData(DataSpec):
        DATASET = {
            'test': {'data_val': 'sample_text'},
            'second_test': {'args': {'data_val': 'sample_text'}, 'meta': {'network': 'yes'}
        }

        def sample_data(self, data_val):
            expect(data_val).to.equal('sample_text')

By doing this, only the 'second_test' will contain metadata. It is important to remember that you can use this format in conjunction with standard metadata tags as mentioned above.


Skipping Tests
~~~~~~~~~~~~~~~~~~
Specter provided a few different ways of skipping tests.

.. autofunction:: specter.skip
   :no-index:
.. autofunction:: specter.skip_if
   :no-index:
.. autofunction:: specter.incomplete()
   :no-index:


Adding Metadata to Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Specter allows for you to tag tests with metadata. The primary purpose of this is to be able to carry misc information along with your test. At some point in the future, Specter will be able to output this information for consumption and processing. However, currently, metadata information can be used to select which tests you want to run.

.. autofunction:: specter.metadata
   :no-index:
