from __future__ import absolute_import
from json import loads as json_loads_fallback
from json import dumps as json_dumps_fallback
try:
    import ujson as json
except ImportError:
    import json
import xml.etree.ElementTree as ElementTree
import codecs
import inspect
import logging
import random
import string
import time
import copy
import requests

import six

import hammock.exceptions as exceptions

URL_PARAMS_METHODS = {'GET', 'HEAD', 'DELETE'}
KW_CONTENT = '_content'
KW_HEADERS = '_headers'
KW_CREDENTIALS = '_credentials'
KW_ENFORCER = '_enforcer'
KW_FILE = '_file'
KW_LIST = '_list'
KW_STATUS = '_status'
KW_HOST = '_host'
CONTENT_TYPE = 'CONTENT-TYPE'
CONTENT_LENGTH = 'CONTENT-LENGTH'
TYPE_JSON = 'application/json'
TYPE_XML = 'application/xml'
TYPE_TEXT_PLAIN = 'text/plain'
TYPE_OCTET_STREAM = 'application/octet-stream'
TOKEN_ENTRY = 'X-Auth-Token'
ID_LETTERS = (string.lowercase if six.PY2 else string.ascii_lowercase) + string.digits
ENCODING = 'utf-8'


# REST method names
PUT = 'PUT'
GET = 'GET'
POST = 'POST'
HEAD = 'HEAD'
DELETE = 'DELETE'
PATCH = 'PATCH'


def json_loads(body):
    """Primary json parser (ujson) is known to have problems
    converting large numbers that cause ValueError on loads operations.
    Fallback to the standard json parser which does not have this issue.
    """
    try:
        return json.loads(body)
    except ValueError:
        return json_loads_fallback(body)


def json_dumps(data):
    """Primary json parser (ujson) is known to have problems
    converting large numbers that cause OverflowError on dumps operations.
    Fallback to the standard json parser which does not have this issue.
    """
    try:
        return json.dumps(data)
    except OverflowError:
        return json_dumps_fallback(data)

CONTENT_CONVERSION = {TYPE_JSON: json_dumps, TYPE_XML: ElementTree.tostring}


def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


def get_exception_message(exc):
    if not isinstance(exc, Exception):
        return None
    if isinstance(exc, requests.exceptions.HTTPError):
        reason = exc.response.content
        try:
            reason = json.loads(reason)['description']  # In case that the HttpError was generated by hammock service
        except:
            pass
        return reason
    else:
        return exc.message


def log_exception(exc, request_uuid):
    if isinstance(exc, exceptions.HttpError):
        logging.warning("[Http %s Exception %s] %s - %s", exc.status, request_uuid, exc.title, exc.description)
    elif isinstance(exc, requests.exceptions.HTTPError):
        logging.exception(get_exception_message(exc))
    else:
        logging.exception("[Internal server error %s]", request_uuid)


def log_request(request_method, request_uri, resp_status, request_start):
    duration_msec = (time.time() - request_start) * 1000
    log_level = logging.INFO
    if request_method.upper() == 'GET' and 200 <= int(resp_status) <= 299:
        log_level = logging.DEBUG
    logging.log(log_level, "%(method)s %(route)s => returned %(retval)s in %(duration).2f msecs",
                dict(method=request_method, route=request_uri,
                     retval=resp_status, duration=duration_msec))


def is_valid_proxy_func(func):
    """
    Checks if a given function is valid for proxy endpoints.
    func should be either empty ('pass') or a generator
    """
    if inspect.isgeneratorfunction(func):
        return True

    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    return empty


def uid(length=8):
    return ''.join(random.sample(ID_LETTERS, length))


def to_bytes(source):
    if isinstance(source, six.string_types):
        return codecs.encode(source, ENCODING)
    elif isinstance(source, six.moves.StringIO):
        # XXX: maybe more efficient way then reading StringIO data.
        return codecs.encode(source.getvalue(), ENCODING)
    return source


def repr_request_kwargs_for_logging(kwargs):
    """
    Request kwargs representation for logging purposes
    :param kwargs: dict
    :return: str representing kwargs for logging
    """
    kw = copy.deepcopy(kwargs)
    # token is too large to be printed
    if KW_CREDENTIALS in kw:
        kw[KW_CREDENTIALS].token = 'omitted'
    return json_dumps(kw)
