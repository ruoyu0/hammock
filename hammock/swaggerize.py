from __future__ import absolute_import
from __future__ import print_function
import six
import argparse
import yaml
import sys
import re

import hammock.packages as packages
import hammock.common as common
import hammock.types.args as _args
import hammock.names as names
import hammock.mock_import as mock_import

from collections import OrderedDict
from hammock.names import PATH_VARIABLE

SWAGGER_TYPES = {
    "str": "string",
    "int": "integer",
}


def strip_escaped_newlines(doc):
    if not doc:
        return ''
    return re.sub('(\\\\n)*$', '', re.sub('^(\\\\n)*', '', doc)).strip()


def _generate_param_dict(route, name, arg, where, required):
    return {
        'name': route.keyword_map.get(name, name),
        'in': where,
        'type': SWAGGER_TYPES.get(arg.type_name, "string"),
        'description': strip_escaped_newlines(arg.doc),
        'required': required,
    }


def generate_swagger(package):
    doc = OrderedDict(
        swagger='2.0',
        info={
            'title': package,
            'version': '1.0.0',
        }
    )
    paths = dict()
    definitions = {}
    with mock_import.mock_import([package]):
        for resource_class, parents in packages.iter_resource_classes(package):
            resource_path = common.url_join(*([parent.path for parent in parents] + [resource_class.path()]))
            for route in resource_class.iter_route_methods():
                path = '/' + common.url_join(resource_path, route.path)
                path_vars = PATH_VARIABLE.findall(path)
                method = route.method.lower()

                # classify params by source: path, query or body
                params = dict()
                for name, arg in six.iteritems(route.spec.args_info):
                    if name.startswith('_'):
                        continue
                    if name in path_vars:
                        params.setdefault('path', dict())[name] = arg
                    elif method in ['get']:
                        params.setdefault('query', dict())[name] = arg
                    elif method in ['post', 'put', 'patch']:
                        params.setdefault('body', dict())[name] = arg

                parameters = []
                # add all path params
                for name, arg in six.iteritems(params.get('path', {})):
                    parameters.append(_generate_param_dict(route, name, arg, 'path', True))

                # add all query params
                for name, arg in six.iteritems(params.get('query', {})):
                    required = not isinstance(arg, (_args.KeywordArg, _args.OptionalArg))
                    parameters.append(_generate_param_dict(route, name, arg, 'query', required))

                # add body param if needed
                properties = {}
                required = []
                for name, arg in six.iteritems(params.get('body', {})):
                    prop_name = route.keyword_map.get(name, name)
                    properties[prop_name] = {
                        'type': SWAGGER_TYPES.get(arg.type_name, "string"),
                        'description': strip_escaped_newlines(arg.doc),
                    }
                    if not isinstance(arg, (_args.KeywordArg, _args.OptionalArg)):
                        required.append(prop_name)
                operation_id = _build_operation_id(parents, resource_class, route)
                if not operation_id:
                    continue
                if len(properties) > 0:
                    param_name = operation_id + '_object'
                    param = {
                        'name': param_name,
                        'in': 'body',
                        'schema': {
                            '$ref': '#/definitions/' + param_name,
                        }
                    }
                    parameters.append(param)
                    definitions[param_name] = dict(type='object', properties=properties)
                    if len(required) > 1:
                        definitions[param_name]['required'] = required
                operation = {
                    'description': strip_escaped_newlines(route.spec.doc),
                    'parameters': parameters,
                    'responses': {
                        route.success_code: {
                            'description': 'default response'
                        }
                    }
                }
                paths.setdefault(path, dict())[method] = operation
    doc['paths'] = paths
    doc['definitions'] = definitions
    return doc


def _build_operation_id(parents, resource_class, route_method):
    return _join_hierarchy(parents, resource_class, route_method, sep='_')


def _build_cli_command(parents, resource_class, route_method):
    return _join_hierarchy(parents, resource_class, route_method, sep=' ')


def _join_hierarchy(parents, resource_class, route_method, sep):
    if (
        route_method is False or
        resource_class.cli_command_name() is False or
        any((parent.cli_command_name is False for parent in parents))
    ):
        return None
    command = [parent.cli_command_name for parent in parents] + [
        resource_class.cli_command_name(),
        route_method.cli_command_name or names.to_command(route_method.__name__),
    ]
    return sep.join(command)


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    args = parser.parse_args()
    parser.add_mutually_exclusive_group()
    doc = generate_swagger(args.package)
    yaml.add_representer(OrderedDict, represent_ordereddict)
    yaml.dump(doc, sys.stdout, default_flow_style=False)


if __name__ == '__main__':
    main()
