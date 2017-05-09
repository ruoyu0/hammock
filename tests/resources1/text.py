from __future__ import absolute_import
import hammock


class Text(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get("upper/{text}")
    def upper(self, text):  # pylint: disable=unused-argument
        """
        Upper.
        :param str text: Text
        :return str: Upper case string
        """
        return text.upper()

    @hammock.get("replace/{text}")
    def replace(self, text, old, new):  # pylint: disable=unused-argument
        """
        Replace.
        :param str text: Text
        :param str old: Old
        :param str new: New
        :return str: New
        """
        return text.replace(old, new)

    @hammock.put("replace/{text}")
    def replace_put(self, text, old, new):  # pylint: disable=unused-argument
        """
        Replace put.
        :param str text: Text
        :param str old: Old
        :param str new: New
        """
        return text.replace(old, new)

    @hammock.post("replace/{text}")
    def replace_post(self, text, old, new):  # pylint: disable=unused-argument
        """
        Replace post.
        :param str text: Text
        :param str old: Old
        :param str new: New
        """
        return text.replace(old, new)

    @hammock.delete("replace/{text}")
    def replace_delete(self, text, old, new):  # pylint: disable=unused-argument
        """
        Replace delete.
        :param str text: Text
        :param str old: Old
        :param str new: New
        """
        return text.replace(old, new)

    @hammock.get("raise-exception")
    def raise_exception(self):  # pylint: disable=unused-argument
        """
        Raise exception.
        :return str: Actually raises an exception
        """
        raise Exception("This exeption is intentional")

    @hammock.get("replace2/{text}")
    def replace2(self, text, old, new):  # pylint: disable=unused-argument
        """
        This method calls another method in a resource.
        :param str text: Text
        :param str old: Old
        :param str new: New
        :return str: Replaced text
        """
        return self.replace(text, old, new)
