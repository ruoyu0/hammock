from __future__ import absolute_import
import hammock
import hammock.common as common


class Headers(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get("{key}")
    def request_headers(self, key, value, _headers):
        """
        Request headers.
        :param str key: Key
        :param str value: Value
        :return bool: Equals?
        """
        return _headers(key) == value

    @hammock.get()
    def response_headers(self, _headers):
        """
        Response headers.
        :return dict: Values
        """
        return {common.KW_HEADERS: _headers}
