.. -*- coding: utf-8 -*-

.. role:: raw-html(raw)
   :format: html

Writing Spektrum Tests
######################

Naming Rules
~~~~~~~~~~~~~~~~~
Most frameworks require you to start your test with a given prefix such as :raw-html:`"test_"`. Spektrum does not impose any prefix rules on test functions. We believe that it is better to give the developer more flexibility in naming so that their test names better describe what they are actually testing. However, Spektrum does have a few rules that should be followed.

* All helper functions should start with an underscore (_). Just as Python treats a single underscore as "protected", so does Spektrum.
* "before_each", "after_each", "before_all", and "after_all" are reserved for setup functions on your test suites (Specs).
* Currently, we also treat "serialize" and "execute" as reserved names as well.


Writing Tests
~~~~~~~~~~~~~~
Writing a test in Spektrum is simple.

1. Create a class which extends Spec
2. Create a function in that class that calls expect or require once

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from spektrum import Spec, expect

    class SampleSpec(Spec):
        """Docstring describing the specification"""
        def it_can_create_an_object(self):
            """ Test docstring"""
            expect('something').to.equal('something')

Test Setup / Teardown
~~~~~~~~~~~~~~~~~~~~~~
:raw-html:`<i>Example:</i>`

.. code-block:: python

    from spektrum import Spec, expect

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
Spektrum tests utilizes the concept of nested test suites. This allows for you to provide a clearer picture of what you are testing within your test suites. For those who have used Jasmine or RSpec should be relatively familiar with this concept from their implementation of Spec.

Within Spektrum you can create a nested test description (suite) in the form of a class that inherits from the Spec class.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from spektrum import Spec, expect

    class SampleSpec(Spec):

        class OtherFunctionalityOfSample(Spec):
            """ Docstring goes here """

            def it_should_do_something(self):
                """ Test Docstring """
                expect('trace').to.equal('trace')


Test Fixtures
~~~~~~~~~~~~~~
In Spektrum, a test fixture is defined as a test base class that is not treated as a runnable test specification. This allows for you to build reusable test suites through inheritance. To facilitate this, there is a decorator named "fixture" available in the spec module.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from spektrum import Spec, fixture, expect

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


Test State and Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each test spec executes its tests under a clean state that does not contain the attributes of the actual Spec class. This allows for users to not worry about conflicting with the Spektrum infrastructure. However, the drawback to this is that the instance of "self" within a test is not actually an instance of the type defined in your hardcoded tests. This makes calling super a little bit unconventional as you can see in the example below.

.. code-block:: python

    from spektrum import Spec

    class FirstSpec(Spec):
        def before_all(self):
            # Do something
            pass

    class SecondSpec(FirstSpec):
        def before_all(self):
            # self is actually an instance of the state object and not an instance of SecondSpec
            super(type(self), self).before_all()

            # Do something else

As you can see in the example, you still can inherit the attributes of your other spec classes. However, you just have to keep in mind, that "self" is actually the state object and not the actual instance of the spec.


Assertions / Expectations
~~~~~~~~~~~~~~~~~~~~~~~~~~
Assertions or expectations in spektrum attempt to be as expressive as possible. This allows for cleaner and more expressive tests which can help with overall code-awareness and effectiveness. It is important to note that an expectation does not fast-fail the test; it will continue executing the test even if the expectation fails.

Expecations follow this flow
    expect [target object] [to or not_to] [comparison] [expected object]

If you were expecting a status_code object was equal to 200 you would write:
    expect(request.status_code).to.equal(200)

Available Comparisons
^^^^^^^^^^^^^^^^^^^^^^^
    * equal(expected_object)
    * almost_equal(expected_number, places)
    * be_greater_than(expected_object)
    * be_less_than(expected_object)
    * be_none()
    * be_true()
    * be_false()
    * be_a(expected_object_type)
    * be_an_instance_of(expected_object_type)
    * be_in(expected_object)
    * contain(expected_object)
    * raise_a(expected_exception_type)

Asserting a raised exception
-----------------------------
.. code::

    expect(example_func, ['args_here']).to.raise_a(Exception)


Fast-fail expectations
^^^^^^^^^^^^^^^^^^^^^^^
In some cases, you need to stop the execution of a test immediately upon the failure of an expectation. With spektrum, we call these requirements. While they follow the same flow as expectations, the name for this action is "require".

Lets say you are writing a test that checks for valid content within a request body. You could do something like:

.. code-block:: python

    expect(request.status_code).to.equal(200)
    require(request.content).not_to.be_none()
    # ... continue processing content

Utilizing this concept can allow for better visibility into an issue when a test fails. For example, if in the given example, the request status code was 202, but the rest of the test passes, you will instantly can see the problem is with the response code and not the body of the message. This has the ability to save you quite a bit of time; especially if you are testing web APIs.


Data-Driven Tests
~~~~~~~~~~~~~~~~~~
Often times you find that you need to run numerous types of data through a given test case. Rather than having to duplicate your tests a large number of times, you can utilize the concept of Data-Driven Tests. This will allow for you to subject your test cases to specified dataset.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from spektrum import DataSpec

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

    from spektrum import DataSpec

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

    from spektrum import DataSpec

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
Spektrum provided a few different ways of skipping tests.

.. autofunction:: spektrum.skip
.. autofunction:: spektrum.skip_if
.. autofunction:: spektrum.incomplete()


Adding Metadata to Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Spektrum allows for you to tag tests with metadata. The primary purpose of this is to be able to carry misc information along with your test. At some point in the future, Spektrum will be able to output this information for consumption and processing. However, currently, metadata information can be used to select which tests you want to run.

.. autofunction:: spektrum.metadata
