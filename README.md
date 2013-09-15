## Specter
#### Keeping the boogy man away from your code!


Specter is a Python testing library inspired from RSpec and Jasmine. Specter is rather new and quite unstable. 
While I encourage people to work with and contribute to the project, please keep in mind that the library may change drastically between versions.

### Example

**Test folder structure:**<br/>
Project Base Folder:<br/>
 \\_ code package<br/>
 \\___ awesome_app.py <br/>
 \\_ spec<br/>
 \\___ some_spec_name.py<br/>

```python
from specter.spec import Describe, Spec
from specter.expect import expect


class ExampleSpec(Spec):
    
    def _random_helper_func(self):
        pass
    
    def this_is_a_test(self):
        """My example doc"""
        expect('bam').to.equal('bam')

    class ChildFunctionality(Describe):
        def before_each(self):
            pass

        def after_each(self):
            pass

        def it_should_do_xxxx(self):
            """More Docs"""
            expect('tosh').to.equal('posh')
            expect(32).not_to.be_less_than(12)

        def it_should_also_do_zzzz(self):
            """Lovely doc strings"""
            expect(100).not_to.be_less_than(99)
```