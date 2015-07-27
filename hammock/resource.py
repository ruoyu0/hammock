import hammock.route as route
import hammock.common as common
import collections
import logging
import functools


TOKEN_ENTRY = "X-Auth-Token"
CONTENT_TYPE = route.CONTENT_TYPE
TYPE_JSON = route.TYPE_JSON
TYPE_OCTET_STREAM = route.TYPE_OCTET_STREAM
KW_HEADERS = route.KW_HEADERS


class Resource(object):

    def __init__(self, api, base_path):
        self._api = api
        self._add_route_methods(base_path)

    def _add_route_methods(self, base_path):
        paths = collections.defaultdict(dict)
        for method in route.iter_route_methods(self):
            paths[method.path]["on_%s" % method.method.lower()] = functools.partial(method.responder, self)
        for path, methods in paths.iteritems():
            new_route = type(
                "_".join([
                    "Resource",
                    base_path.replace("/", "_"),
                    self.name().capitalize(),
                    path.translate(None, "{}/."),
                    ]),
                (), methods)()
            self._api.add_route("/%s" % common.url_join(base_path, self.name(), path), new_route)
        logging.debug("Added %s to api", self.name())

    @classmethod
    def name(cls):
        return cls.__name__.lower()


def get(path="", **kwargs):
    return route.route(path, "GET", **kwargs)


def post(path="", **kwargs):
    return route.route(path, "POST", **kwargs)


def put(path="", **kwargs):
    return route.route(path, "PUT", **kwargs)


def delete(path="", **kwargs):
    return route.route(path, "DELETE", **kwargs)
