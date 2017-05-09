from __future__ import absolute_import
import hammock


class CLIIgnoredResource(hammock.Resource):
    POLICY_GROUP_NAME = False
    CLI_COMMAND_NAME = False

    @hammock.get()
    def get(self):
        """
        Get.
        :return str: CLI-ignored-resource
        """
        return 'cli-ignored-resource'
