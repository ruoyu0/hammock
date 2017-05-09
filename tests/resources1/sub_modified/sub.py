from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):
    PATH = "different-sub"
    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self):
        """
        Get.
        :return str: A constant string
        """
        return "modified-in-modified"

    @hammock.post(cli_command_name='post-modified')
    def post(self):
        """
        Post.
        """
        return "modified-in-modified-in-modified"
