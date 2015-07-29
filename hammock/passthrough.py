import logging
import requests
import urlparse
import uuid
import hammock.common as common
import hammock.types as types


def passthrough(request, response, dest, pre_process, post_process, trim_prefix, func, **params):
    request_uuid = uuid.uuid4()
    logging.info("[Passthrough received %s] requested: %s", request_uuid, request.url)
    try:
        if trim_prefix:
            _trim_prefix(request, trim_prefix)
        if pre_process:
            pre_process(request, **params)
        if dest:
            output = _passthrough(request, dest, request_uuid)
        else:
            output = func(request, **params)
        if post_process:
            output = post_process(output, **params)
        body_or_stream, response._headers, response.status = output
        response.status = str(response.status)
        if hasattr(body_or_stream, "read"):
            response.stream = body_or_stream
        else:
            response.body = body_or_stream
    except Exception as e:
        logging.exception("[Passthrough error %s]", request_uuid)  # this will show traceback in logs
        e = common.convert_exception(e)
        response.status, response.body = e.status, e.to_dict()  # assingment for logging in finally block
        raise e
    finally:
        logging.debug(
            "[Passthrough response %s] status: %s, body: %s",
            request_uuid, response.status, response.body,
        )


def _passthrough(request, dest, request_uuid):
    redirection_url = common.url_join(dest, request.path)
    logging.info("[Passthrough %s] redirecting to %s", request_uuid, redirection_url)
    inner_request = requests.Request(
        request.method,
        url=redirection_url,
        data=request.stream if request.method in ("POST", "PUT", "PATCH") else None,
        headers={
            k: v if k.lower() != "host" else urlparse.urlparse(dest).netloc
            for k, v in request.headers.iteritems()
            if v != ""
        },
    )
    session = requests.Session()
    try:
        prepared = session.prepare_request(inner_request)
        if request.headers.get('CONTENT-LENGTH'):
            prepared.headers['CONTENT-LENGTH'] = request.headers.get('CONTENT-LENGTH')
        if request.headers.get('TRANSFER-ENCODING'):
            del prepared.headers['TRANSFER-ENCODING']
        inner_response = session.send(prepared, stream=True)
        return types.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
    finally:
        session.close()


def _trim_prefix(request, trim_prefix):
    request.path = request.path.lstrip("/")[len(trim_prefix.strip("/")):]
