.. role:: raw-html(raw)
   :format: html

Writing Specter Tests
######################

Naming Rules
~~~~~~~~~~~~~~~~~
Most frameworks require you to start your test with a given prefix such as :raw-html:`"test_"`. Specter does not impose any prefix rules on test functions. We believe that it is better to give the developer more flexibility in naming so that their test names better describe what they are actually testing. However, while Specter does have three rules that should be followed.

* All helper functions should start with an underscore (_). Just as Python treats a single underscore as "protected", so does Specter.
* The name "execute" is restricted. This name is used by internally by Specter, so do not use it in your test function names.
* "before_each" and "after_each" are reserved for setup functions on your test suites (Specs or Decribes).


Writing Tests
~~~~~~~~~~~~~~
Writing a test in Specter is simple.
1. Create a class which extends Spec or Describe
2. Create a function in that class that calls expect or require once

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter.spec import Spec
    from specter.expect import expect

    class SampleSpec(Spec):
        """Docstring describing the specification"""
        def it_can_create_an_object(self):
            """ Test docstring"""
            expect('something').to.equal('something')

Test Setup / Teardown
~~~~~~~~~~~~~~~~~~~~~~
:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter.spec import Spec
    from specter.expect import expect

    class SampleSpec(Spec):
        """Docstring describing the specification"""

        def before_each(self):
            pass

        def after_each(self):
            pass

        def it_can_create_an_object(self):
            """ Test docstring"""
            expect('something').to.equal('something')


Nested Tests
~~~~~~~~~~~~~~
Specter tests utilizes the concept of nested test suites. This allows for you to provide a clearer picture of what you are testing within your test suites. For those who have used Jasmine or RSpec should be relatively familiar with this concept from their implementation of Describe and Spec.

Within Specter you can create a nested test description (suite) in the form of a class that inherits from the Describe class.

:raw-html:`<i>Example:</i>`

.. code-block:: python

    from specter.spec import Describe, Spec
    from specter.expect import expect

    class SampleSpec(Spec):

        class OtherFunctionalityOfSample(Describe):
            """ Describe Docstring """

            def it_should_do_something(self):
                """ Test Docstring """
                expect('trace').to.equal('trace')


Assertions / Expectations
~~~~~~~~~~~~~~~~~~~~~~~~~~
Assertions or expectations in specter attempt to be as expressive as possible. This allows for cleaner and more expressive tests which can help with overall code-awareness and effectiveness. It is important to note that an expectation does not fast-fail the test; it will continue executing the test even if the expectation fails.

Expecations follow this flow
    expect [target object] [to or not_to] [comparison] [expected object]

If you were expecting a status_code object was equal to 200 you would write:
    expect(request.status_code).to.equal(200)

Available Comparisons
^^^^^^^^^^^^^^^^^^^^^^^
    * equal(expected_object)
    * be_greater_than(expected_object)
    * be_less_than(expected_object)
    * be_none()
    * be_true()
    * be_false()
    * contain(expected_object):

Fast-fail expectations
^^^^^^^^^^^^^^^^^^^^^^^
In some cases, you need to stop the execution of a test immediately upon the failure of an expectation. With specter, we call these requirements. While they follow the same flow as expectations, the name for this action is "require".

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

    class ExampleDataDescribe(DataDescribe):
        DATASET = {
            'test': {'data_val': 'sample_text'},
            'second_test': {'data_val': 'sample_text'}
        }

        def sample_data(self, data_val):
            expect(arg).to.equal('sample_text')

This dataset will produce a Describe with two tests: "sample_data_test" and "sample_data_second_test" each passed in "sample_text" under the data_val parameter.

:raw-html:`<i>This would produce a console output similar to:</i>`

.. code-block:: bash

    ExampleDataDescribe
      ∟ sample data test
        ∟ expect "sample_text" to equal "sample_text"
      ∟ sample data second test
        ∟ expect "sample_text" to equal "sample_text"  