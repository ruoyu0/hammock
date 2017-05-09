from __future__ import absolute_import
import hammock


class Empty(hammock.Resource):

    POLICY_GROUP_NAME = False
    PATH = ''

    @hammock.get('additional')
    def additional(self):
        """
        Additional.
        :return str: Additional
        """
        return 'additional'

    @hammock.get('additional-2')
    def additional_2(self):
        """
        Additional 2.
        :return str: Additional-2
        """
        return 'additional-2'
