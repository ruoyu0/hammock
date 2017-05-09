from __future__ import absolute_import
import hammock
import hammock.exceptions as exceptions

DESCRIPTION = 'This exception is intentional'


class Exceptions(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get('internal')
    def internal(self):
        """
        Internal.
        :return str: Nothing
        """
        raise Exception(DESCRIPTION)

    @hammock.get('not-found')
    def not_found(self):
        """
        Not found.
        :return str: Nothing
        """
        raise exceptions.NotFound(DESCRIPTION)
