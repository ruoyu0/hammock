from __future__ import absolute_import
import hammock


class Lists(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get('{path}')
    def get(self, path, argument):
        """
        Get.
        :param str path: Path
        :return dict: Values
        """
        return {
            'path': int(path),
            'argument': [int(ai) for ai in argument],
        }

    @hammock.post('{path}')
    def append(self, path, _list):
        """
        Append to a list.
        :param int path: Append to list
        :param list _list: List to append to
        :return list: The list with extra value
        """
        _list.append(int(path))
        return _list
