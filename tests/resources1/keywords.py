from __future__ import absolute_import
import hammock


class Keywords(hammock.Resource):

    DEFAULT = 10
    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self, arg, default=DEFAULT, **kwargs):
        """
        Get.
        :param str arg: Arg
        :param str default: Default
        :return dict: Answer
        """
        return self._answer(arg, default, **kwargs)

    @hammock.post()
    def post(self, arg, default=DEFAULT, **kwargs):
        """
        Post.
        :param int arg: Arg
        :param int default: Default
        """
        return self._answer(arg, default, **kwargs)

    @hammock.put()
    def put(self, arg, default=DEFAULT, **kwargs):
        """
        Put.
        :param int arg: Arg
        :param int default: Default
        """
        return self._answer(arg, default, **kwargs)

    @hammock.get("headers")
    def get_with_headers(self, arg, _headers, default=10, **kwargs):
        """
        Get with headers.
        :param str arg: Arg
        :param str default: Default
        :return dict: Answer
        """
        return self._answer(arg, default, headers=dict(_headers), **kwargs)

    def _answer(self, arg, default, **kwargs):
        ret = {
            "arg": arg,
            "default": default,
        }
        ret.update(kwargs)
        return ret
