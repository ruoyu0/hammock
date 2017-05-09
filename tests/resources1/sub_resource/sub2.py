from __future__ import absolute_import
import hammock


class Sub2(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self):
        """
        Get.
        :return str: String
        """
        return "sub2-in-sub1"
