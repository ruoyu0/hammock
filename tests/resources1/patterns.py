from __future__ import absolute_import
import six
import hammock
import hammock.common as common


class Patterns(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self):
        """
        Get.
        :return str: A constant string
        """
        return "base"

    @hammock.get("{my_id}")
    def get_id(self, my_id):
        """
        Get ID.
        :param str my_id: My ID
        :return str: ID
        """
        return "id-%s" % my_id

    @hammock.sink("{my_id}/extra")
    def get_id_metadata(self, request, my_id):  # pylint: disable=unused-argument
        return hammock.types.Response(
            content=six.BytesIO(six.b(common.json_dumps('extra-%s') % my_id)),
            status=200,
            headers={common.CONTENT_TYPE: common.TYPE_JSON},
        )

    @hammock.sink("{my_id}/extra/specific")
    def get_id_metadata_specific(self, request, my_id):  # pylint: disable=unused-argument
        return hammock.types.Response(
            content=six.BytesIO(six.b(common.json_dumps('extra-specific-%s') % my_id)),
            status=200,
            headers={common.CONTENT_TYPE: common.TYPE_JSON},
        )
