from __future__ import absolute_import
import six
import falcon
import inspect
import functools
import simplejson as json
import logging
import uuid
import hammock.common as common
import hammock.types as types
import hammock.passthrough as passthrough_module

KW_HEADERS = common.KW_HEADERS


def route(path, method, client_methods=None, success_code=200, response_content_type=common.TYPE_JSON, exception_handler=None):
    def _decorator(func):
        spec = types.FuncSpec(func)
        func.is_route = True
        func.path = path
        func.method = method
        func.client_methods = client_methods
        func.success_code = success_code if isinstance(success_code, int) \
            else int(success_code.split(" ")[0])  # pylint: disable=maybe-no-member
        func.response_content_type = response_content_type

        @functools.wraps(func)
        def _wrapper(self, request, response, **url_kwargs):
            request_uuid = uuid.uuid4()
            logging.debug(
                "[request %s] %s %s",
                request_uuid, request.method, request.url)
            try:
                request_params = _extract_params(request)
                request_headers = types.Headers(request.headers)
                kwargs = _convert_to_kwargs(spec, url_kwargs, request_params, request_headers)
            except Exception as e:  # pylint: disable=broad-except
                logging.warning("[Error parsing request kwargs %s] %s", request_uuid, e)
                self.handle_exception(e, exception_handler)
            else:
                logging.debug("[kwargs %s] %s", request_uuid, kwargs)
            try:
                result = func(self, **kwargs)
                if result is not None:
                    _extract_response_headers(result, response)
                    _extract_response_body(result, response, response_content_type)
            except Exception as e:  # pylint: disable=broad-except
                common.log_exception(e, request_uuid)
                self.handle_exception(e, exception_handler)
            else:
                response.status = str(success_code)
                logging.debug(
                    "[response %s] status: %s, body: %s",
                    request_uuid, response.status, response.body,
                )

        func.responder = _wrapper
        return func
    return _decorator


def passthrough(path, method, dest, pre_process=None, post_process=None, trim_prefix=False, exception_handler=None):
    def _decorator(func):
        func.is_route = True
        func.path = path
        func.method = method
        func.client_methods = {}
        func.success_code = None
        func.response_content_type = None

        @functools.wraps(func)
        def _wrapper(self, request, response, **params):
            passthrough_module.passthrough(
                self,
                request,
                response,
                dest,
                pre_process,
                post_process,
                trim_prefix,
                func,
                exception_handler,
                **params
            )

        func.responder = _wrapper
        return func
    return _decorator


def _extract_params(request):
    params = {
        k: (v if v != "None" else None)
        for k, v in six.iteritems(request.params)
    }
    if request.method not in common.URL_PARAMS_METHODS:
        content_type = request.get_header(common.CONTENT_TYPE)
        if content_type == common.TYPE_JSON:
            try:
                data = json.load(request.stream)
                if type(data) == dict:
                    params.update(data)
                elif type(data) == list:
                    params[common.KW_LIST] = data
            except (ValueError, UnicodeDecodeError):
                raise falcon.HTTPError(
                    falcon.HTTP_753,
                    'Malformed JSON',
                    'Could not decode the request body. The JSON was incorrect or not encoded as UTF-8.'
                )
        elif content_type == common.TYPE_OCTET_STREAM:
            params[common.KW_FILE] = types.File(request.stream, request.get_header(common.CONTENT_LENGTH))
    return params


def _convert_to_kwargs(spec, url_kwargs, request_params, request_headers):
    args = spec.args[:]
    kwargs = request_params or {}
    kwargs.update(url_kwargs or {})
    kwargs.update({
        keyword: kwargs.get(keyword, default)
        for keyword, default in six.iteritems(spec.kwargs)
    })
    if common.KW_HEADERS in spec.args:
        kwargs[common.KW_HEADERS] = request_headers
    for kw, error_msg in (
        (common.KW_FILE, "expected {} as {}".format(common.CONTENT_TYPE, common.TYPE_OCTET_STREAM)),
        (common.KW_LIST, "expected {} {} as list".format(common.CONTENT_TYPE, common.TYPE_JSON)),
            ):
        if kw in args:
            try:
                kwargs[kw] = request_params[kw]
            except KeyError:
                raise falcon.HTTPError(falcon.HTTP_415, 'Bad data', error_msg)
            args.remove(kw)
    missing = set(args) - set(kwargs)
    if missing:
        raise falcon.HTTPBadRequest(
            "Missing parameters: %s" % ", ".join(missing),
            "Bad request")
    return kwargs


def _extract_response_headers(result, response):
    if isinstance(result, dict) and common.KW_HEADERS in result:
        for k, v in six.iteritems(result.pop(common.KW_HEADERS)):
            response.set_header(k, str(v))


def _extract_response_body(result, response, content_type):
    if content_type == common.TYPE_JSON:
        response.body = json.dumps(result)
    elif content_type == common.TYPE_OCTET_STREAM:
        response.stream = result
    else:
        raise Exception("Unsupported response content-type %s", content_type)
    response.set_header(common.CONTENT_TYPE, content_type)


def iter_route_methods(resource_object):
    return (
        attr for _, attr in inspect.getmembers(resource_object)
        if getattr(attr, "is_route", False)
    )