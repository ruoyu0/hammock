from __future__ import absolute_import

import hammock
from hammock import types

PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


def pre_manipulate(request, _):
    body = request.json
    body['some_more_data'] = 'b'
    request.json = body


def post_manipulate(response, _):
    body = response.json
    assert body['body'].pop('some_more_data') == 'b'
    response.json = body


def pre_manipulate_path(request, _):
    request.path = 'a'


def post_manipulate_path(response, _):
    body = response.json
    assert body['path'] == '/a'
    response.json = body


class Redirect(hammock.Resource):

    POLICY_GROUP_NAME = False

    def __init__(self, **kwargs):
        self.before = kwargs.get('before')
        self.after = kwargs.get('after')
        super(Redirect, self).__init__(**kwargs)

    @hammock.sink(dest=DEST, trim_prefix="redirect")
    def passthrough(self):
        pass

    @hammock.get("specific")
    def specific(self):
        """
        Specific.
        :return str: A specific string
        """
        return "specific"

    @hammock.post(
        dest=DEST,
        path='post-passthrough',
        trim_prefix='redirect',
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough(self):
        pass

    @hammock.post(
        dest=None,
        path='post-passthrough-with-body',
        trim_prefix='redirect',
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough_with_body(self, request):
        """
        Post passthrough with body.
        :param str request: Request
        """
        body = {
            'body': request.json,
            'headers': dict(request.headers),
        }
        return types.Response(content=body)

    @hammock.get(
        dest=DEST,
        path='manipulate-path',
        trim_prefix='redirect',
        pre_process=pre_manipulate_path,
        post_process=post_manipulate_path,
    )
    def manipulate_path(self):
        pass

    @hammock.post(
        dest=DEST,
        path='post-generator',
        trim_prefix='redirect',
    )
    def post_generator(self, some_data):
        """
        Post generator.
        :param str some_data: Some data
        """
        self.before(some_data)
        resp = yield
        self.after(resp)

    @hammock.sink(
        dest=DEST,
        path='sink-generator',
        trim_prefix='redirect',
    )
    def sink_generator(self, req):
        self.before(req)
        resp = yield
        self.after(resp)

    @hammock.sink(
        dest=DEST,
        path='sink-generator-with-missing-url-params-kwargs/{param1}/{param2}',
        trim_prefix='redirect',
    )
    def sink_generator_with_missing_url_params_kwargs(self, req, param1):  # pylint: disable=unused-argument
        yield

    @hammock.sink(
        dest=DEST,
        path='sink-generator-with-full-url-params-kwargs/{param1}/{param2}',
        trim_prefix='redirect',
    )
    def sink_generator_with_full_url_params_kwargs(self, req, param1, param2):  # pylint: disable=unused-argument
        self.before(param1, param2)
        yield
