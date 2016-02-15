from __future__ import absolute_import
import requests
import hammock.common as common
import tests.uwsgi_base as uwsgi_base


class TestUwsgiPolicy(uwsgi_base.UwsgiBase):

    def test_policy_no_auth_details(self):
        self.assert_not_authorized(self._client.policy.project_admin)
        self.assert_not_authorized(self._client.policy.admin)

    def test_admin(self):
        admin = self.get_client(headers={
            common.HEADER_ROLE: 'admin'
        })
        self.assertEqual(admin.policy.project_admin(), True)
        self.assertEqual(admin.policy.admin(), True)

    def test_project_admin(self):
        project_admin = self.get_client(headers={
            common.HEADER_ROLE: 'project_admin',
            common.HEADER_PROJECT_ID: 'project-id-1'
        })
        self.assertEqual(project_admin.policy.project_admin(project_id='project-id-1'), True)
        self.assert_not_authorized(project_admin.policy.project_admin, project_id='project-id-2')
        self.assert_not_authorized(project_admin.policy.admin, project_id='project-id-1')

    def assert_not_authorized(self, func, *args, **kwargs):
        with self.assertRaises(requests.HTTPError) as exc:
            func(*args, **kwargs)
        self.assertEqual(exc.exception.response.status_code, 403)
