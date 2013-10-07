.. role:: raw-html(raw)
   :format: html

Writing Specter Tests
######################

Naming Rules
~~~~~~~~~~~~~~~~~
Most frameworks require you to start your test with a given prefix such as :raw-html:`"test_"`. Specter does not impose any prefix rules on test functions. We believe that it is better to give the developer more flexibilty in naming so that their test names better decribe what they are actually testing. However, while Specter does have three rules that should be followed.

* All helper functions should start with an underscore (_). Just with normal python, underscores indicate a "protected" function, as such Specter does not touch those functions.
* The name "execute" is restricted. This name is used by internally by Specter, so do not use it in your test function names.
* "before_each" and "after_each" are reserved for setup functions on your test suites (Specs or Decribes).


Nested Tests
~~~~~~~~~~~~~~
Specter tests utilizes the concept of nested testing.