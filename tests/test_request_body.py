# pylint: disable=W0212
from __future__ import absolute_import
import tests.base as base
import hammock.common as common

from hammock.backends._falcon import Falcon


class TestRequestBody(base.TestBase):

    class TestFalconRequest(object):
        def __init__(self, method, url, headers, content_type, params=None, stream=None):
            self.method = method
            self.url = url
            self.headers = headers
            self.content_type = content_type
            self.params = params
            self.stream = stream
            self.url_params = {}

    def test_url_encoded_body(self):
        params_url_encoded = {
            'Action': 'DescribeInstances',
            'Version': '2016-11-15'
        }
        header_url_encoded = {common.CONTENT_TYPE: common.TYPE_URL_ENCODED}
        backend_req = self.TestFalconRequest(
            "POST", "http://test/", header_url_encoded,
            common.TYPE_URL_ENCODED, params_url_encoded)
        hammock_request = Falcon._req_from_backend(backend_req, {})
        self.assertEqual("Action=DescribeInstances&Version=2016-11-15",
                         hammock_request.content)

        backend_req.params = {}
        hammock_request = Falcon._req_from_backend(backend_req, {})
        self.assertEqual("", hammock_request.content)

        backend_req.headers = {common.CONTENT_TYPE: common.TYPE_JSON}
        backend_req.content_type = common.TYPE_JSON
        test_stream = "This takes place of a streaming object"
        backend_req.stream = test_stream
        hammock_request = Falcon._req_from_backend(backend_req, {})
        self.assertEqual(test_stream, hammock_request.content)
