from __future__ import absolute_import
import hammock
import hammock.exceptions as exceptions

NAMES = {
    'name_with_underscores': 'name-with-underscores',
    'NameWithCamelCase': 'name-with-camel-case',
    'MULTICaps': 'multi-caps',
    'CapsMULTI': 'caps-multi',
}


class CLINames(hammock.Resource):
    POLICY_GROUP_NAME = False

    @hammock.post('optional-variable-with-underscore')
    def optional_variable_with_underscores(self, optional_variable=None):  # pylint: disable=invalid-name
        """
        Returns an optional variable.
        :param str optional_variable: An optional variable
        :return: The optional variable
        """
        return optional_variable

    @hammock.post('set-true')
    def set_true(self, set_true=False):
        """
        Set True.
        :param bool[False] set_true: Set true
        :return bool: Set True?
        """
        return set_true

    @hammock.post('set-false')
    def set_false(self, set_false=True):
        """
        Set False.
        :param bool[True] set_false: Set false
        :return bool: Set False?
        """
        return set_false

    @hammock.post('bool-type')
    def bool_type(self, value=None):
        """
        Return a bool value.
        :param bool value: Value
        :return bool: The value
        """
        if not isinstance(value, bool):
            raise exceptions.BadRequest('Value should be bool')
        return value

    @hammock.get('ignored-method', cli_command_name=False)
    def ignored_method(self):
        """
        Ignored method.
        :return str: Ignored-method
        """
        return 'ignored-method'

    @hammock.get('returns-nothing-type')
    def returns_nothing_type(self):
        """
        Returns nothing type.
        :return None: None
        """
        return 'something'

    @hammock.get('argument-with-underscores')
    def argument_with_underscores(self, _arg_, _second_arg_=None):
        """
        Argument with underscores.
        :param int _arg_: Argument with underscores
        :param int _second_arg_: Second argument with underscores
        :return dict: Parameters
        """
        return {'arg': _arg_, 'second': _second_arg_}


def _get_func(func_name):
    @hammock.get(func_name.replace('_', '-'))
    def func(self):  # pylint: disable=unused-argument
        """
        Func.
        :return str: Func name
        """
        return func_name
    func.__name__ = func_name
    return func


for name in NAMES.keys():
    setattr(CLINames, name, _get_func(name))
