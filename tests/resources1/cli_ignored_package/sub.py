from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):
    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self):
        """
        Get.
        :return str: A constant string
        """
        return "sub-in-ignored"
