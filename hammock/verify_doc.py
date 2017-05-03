"""This script verifies that all APIs and all parameters are documented.
All parameters must have an explict type, and default binary values
are verified as well."""

from __future__ import absolute_import
from __future__ import print_function
import sys
import six
import inspect
import argparse
from collections import namedtuple

import hammock.common as common
import hammock.packages as packages
import hammock.mock_import as mock_import
from hammock.names import PATH_VARIABLE
from hammock.swaggerize import strip_escaped_newlines


NO_DEFAULT = object()

Method = namedtuple('Method', ('name', 'doc', 'class_name', 'method', 'returns', 'returns_doc', 'success_code'))
Argument = namedtuple('Argument', ('name', 'doc', 'class_name', 'method_name', 'type_name', 'default', 'has_default'))


def _verify_argument(identifier, arg, argument_verifier):
    errors = argument_verifier(arg) if argument_verifier else []
    if not arg.doc:
        errors.append('not documented')
    if not arg.type_name:
        errors.append('has no type')

    bool_dict = {'bool': NO_DEFAULT,
                 'bool[True]': True,
                 'bool[False]': False}
    if arg.type_name in bool_dict and bool_dict[arg.type_name] != arg.default:
        errors.append('default does not match documentation')
    if arg.doc and arg.doc[0] != arg.doc[0].upper():
        errors.append('documentation is not capitalized')
    if arg.doc.endswith('.'):
        errors.append('documentation should not end with a .')
    return ['%s %s: %s' % (identifier, arg.name, err) for err in errors]


def _verify_method(identifier, method, method_verifier):
    errors = method_verifier(method) if method_verifier else []
    if not method.doc:
        errors.append('not documented')
    if method.method == 'GET' and not method.returns:
        errors.append('has no return value')
    if method.doc and method.doc[0] != method.doc[0].upper():
        errors.append('documentation is not capitalized')
    if not method.doc.endswith('.'):
        errors.append('documentation should end with a .')
    if method.returns and not method.returns_doc:
        errors.append('no documentation for return value')
    if method.returns_doc.endswith('.'):
        errors.append('documentation of return value should not end with a .')
    if method.returns_doc and method.returns_doc[0] != method.returns_doc[0].upper():
        errors.append('documentation of return value is not capitalized')
    return ['%s: %s' % (identifier, err) for err in errors]


def _func_default_dict(route):
    func_args = inspect.getargspec(route.func).args
    arg_names = [route.keyword_map.get(name, name) for name in func_args]
    defaults = inspect.getargspec(route.func).defaults or tuple()
    defaults = (NO_DEFAULT, ) * (len(arg_names) - len(defaults)) + defaults
    return dict(zip(arg_names, defaults))


def verify_doc(package, method_verifier=None, argument_verifier=None):
    errors = []
    with mock_import.mock_import([package]):
        for resource_class, parents in packages.iter_resource_classes(package):
            resource_path = common.url_join(*([parent.path for parent in parents] + [resource_class.path()]))
            for route in resource_class.iter_route_methods():
                path = '/' + common.url_join(resource_path, route.path)
                identifier = '%s::%s' % (resource_class.__name__, route.func.__name__)
                stripped_path = path[:]
                for path_var in PATH_VARIABLE.findall(path):
                    stripped_path = stripped_path.replace('{%s}' % path_var, '')
                if '_' in stripped_path:
                    errors.append('%s has _ in path (use -)' % identifier)

                method = Method(name=route.func.__name__,
                                doc=strip_escaped_newlines(route.spec.doc),
                                class_name=resource_class.__name__,
                                method=route.method,
                                returns=route.spec.returns,
                                returns_doc=route.spec.returns.doc if route.spec.returns else '',
                                success_code=route.success_code)
                errors.extend(_verify_method(identifier, method, method_verifier))

                default_dict = _func_default_dict(route)
                for name, arg in six.iteritems(route.spec.args_info):
                    if not name.startswith('_'):
                        identifier = '%s::%s' % (resource_class.__name__, route.func.__name__)
                        default = default_dict.get(name, NO_DEFAULT)
                        argument = Argument(name=route.keyword_map.get(name, name),
                                            class_name=resource_class.__name__,
                                            doc=strip_escaped_newlines(arg.doc),
                                            method_name=route.func.__name__,
                                            type_name=arg.type_name,
                                            default=default,
                                            has_default=default is not NO_DEFAULT)
                        errors.extend(_verify_argument(identifier, argument, argument_verifier))

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    args = parser.parse_args()
    parser.add_mutually_exclusive_group()
    errors = verify_doc(args.package)
    sys.stderr.write('\n'.join(errors) + '\n')
    if errors:
        sys.stderr.write('%d errors found in API documentation\n' % len(errors))
    if errors:
        sys.exit(-1)


if __name__ == '__main__':
    main()
