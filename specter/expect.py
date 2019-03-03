import ast
import copy
import inspect

from specter import utils
from specter.spec import Spec
from specter.exceptions import FailedRequireException


class Expectation(object):
    def __init__(self, target, required=False, caller_args=None, caller_kwargs=None):
        self.prefix = 'expect'
        self.success = False
        self.used_negative = False
        self.target = target
        self.required = required
        self.actions = [target]
        self.caller_args = caller_args
        self.caller_kwargs = caller_kwargs
        self.custom_msg = None
        self.custom_report_vars = {}

    def _verify_condition(self, condition):
        self.success = condition if not self.used_negative else not condition
        if self.required and not self.success:
            raise FailedRequireException()

        return self.success

    def _compare(self, action_name, expected, condition):
        self.expected = expected
        self.actions.extend([action_name, expected])
        self._verify_condition(condition=condition)

    def __str__(self):
        action_list = copy.copy(self.actions)
        action_list[-1] = str(self.expected)

        return ' '.join([str(action) for action in action_list])

    @property
    def not_to(self):
        self.actions.append('not')
        self.used_negative = not self.used_negative
        return self.to

    @property
    def to(self):
        self.actions.append('to')
        return self

    def equal(self, expected):
        self._compare(
            action_name='equal',
            expected=expected,
            condition=self.target == expected
        )

    def almost_equal(self, expected, places=7):
        if not isinstance(places, int):
            raise TypeError('Places must be an integer')

        self._compare(
            action_name='almost equal',
            expected=expected,
            condition=round(abs(self.target - expected), places) == 0
        )

    def be_greater_than(self, expected):
        self._compare(
            action_name='be greater than',
            expected=expected,
            condition=self.target > expected
        )

    def be_less_than(self, expected):
        self._compare(
            action_name='be less than',
            expected=expected,
            condition=self.target < expected
        )

    def be_none(self):
        self._compare(
            action_name='be',
            expected=None,
            condition=self.target is None
        )

    def be_true(self):
        self._compare(
            action_name='be',
            expected=True,
            condition=self.target
        )

    def be_false(self):
        self._compare(
            action_name='be',
            expected=False,
            condition=not self.target
        )

    def contain(self, expected):
        self._compare(
            action_name='contain',
            expected=expected,
            condition=expected in self.target
        )

    def be_in(self, expected):
        self._compare(
            action_name='be in',
            expected=expected,
            condition=self.target in expected
        )

    def be_a(self, expected):
        self._compare(
            action_name='be a',
            expected=expected,
            condition=type(self.target) is expected
        )

    def be_an_instance_of(self, expected):
        self._compare(
            action_name='be an instance of',
            expected=expected,
            condition=isinstance(self.target, expected)
        )

    def raise_a(self, exception):
        self.expected = exception
        self.actions.extend(['raise', exception])
        condition = False
        raised_exc = 'nothing'

        try:
            self.target(*self.caller_args, **self.caller_kwargs)
        except Exception as e:
            condition = type(e) == exception
            raised_exc = e

        # We didn't raise anything
        if self.used_negative and not isinstance(raised_exc, Exception):
            self.success = True

        # Raised, but it didn't match
        elif self.used_negative and type(raised_exc) != exception:
            self.success = False

        elif self.used_negative:
            self.success = not condition

        else:
            self.success = condition

        if not self.success:
            was = 'wasn\'t' if self.used_negative else 'was'

            # Make sure we have a name to use
            if getattr(self.expected, '__name__'):
                name = self.expected.__name__
            else:
                name = type(self.expected).__name__

            self.custom_msg = f'function {was} expected to raise "{name}".'
            # self.custom_report_vars['Raised Exception'] = (
            #     type(raised_exc).__name__
            # )


class Requirement(Expectation):
    def __init__(self, target, required=True, caller_args=None, caller_kwargs=None):
        super().__init__(
            target=target,
            required=required,
            caller_args=caller_args,
            caller_kwargs=caller_kwargs,
        )
        self.prefix = 'require'


def _find_last_spec():
    for frame, *_ in inspect.stack():
        obj = frame.f_locals.get('self')
        if obj and isinstance(obj, Spec):
            return obj, frame


def _add_expect_to_spec(instance):
    """Walks the stack back until it gets to a Spec and adds the expectation"""
    try:
        spec, frame = _find_last_spec()
        # HACK(jmvrbanac): Oooo this is nasty!
        func = frame.f_back.f_locals['method'].__func__
        spec.__expects__[func].append(instance)

    except Exception as error:
        raise Exception(
            f'Error attempting to add expect to parent Spec: {error}'
        )



def _get_closest_expression(line, tree):
    def distance(node):
        return abs(node.lineno - line)

    # Walk the tree until we get the expression we need
    expect_exp = None
    closest_exp = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            if node.lineno == line:
                expect_exp = node
                break

            if (closest_exp is None
                    or distance(node) < distance(closest_exp)):
                closest_exp = node

    return expect_exp or closest_exp


def get_module_and_line(use_child_attr=None):
    spec, frame = _find_last_spec()
    source_filename = frame.f_code.co_filename
    func = getattr(spec, frame.f_code.co_name)
    source, node = utils.load_source_and_ast(source_filename)

    # expr_node = _get_closest_expression(frame.f_lineno, node)
    # expr = ExpectExpression(expr_node)

    #  = astor.parse_file(source_filename)
    # last_frame = inspect.currentframe()
    # test_case_frame = last_frame.f_back.f_back

    # import pdb; pdb.set_trace()
    return None, None


def expect(obj, caller_args=None, **kwargs):
    """Primary method for test assertions in Specter

    :param obj: The evaluated target object
    :param caller_args: Is only used when using expecting a raised Exception
    :param **kwargs: Kwargs passed through to the function.
    """
    # line, module = get_module_and_line()
    # src_params = ExpectParams(line, module)
    obj = Expectation(obj, caller_args=caller_args or [], caller_kwargs=kwargs)
    _add_expect_to_spec(obj)
    return obj


def require(obj, caller_args=None, **kwargs):
    """Primary method for test assertions in Specter

    :param obj: The evaluated target object
    :param caller_args: Is only used when using expecting a raised Exception
    :param **kwargs: Kwargs passed through to the function.
    """
    # line, module = get_module_and_line('__spec__')
    # src_params = ExpectParams(line, module)

    obj = Requirement(obj, caller_args=caller_args or [], caller_kwargs=kwargs)
    _add_expect_to_spec(obj)
    return obj
