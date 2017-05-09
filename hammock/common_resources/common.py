from __future__ import absolute_import
import hammock
import hammock.client as client
import hammock.doc as doc


class CommonResources(hammock.Resource):

    PATH = ''
    POLICY_GROUP_NAME = False

    @hammock.get('_client', response_content_type='text/x-python')
    def get_client(self, _host):
        verification_exceptions = (('ArgumentTypes', 'conversions_in_get', 'not_in_doc'),
                                   ('ArgumentTypes', 'conversions_in_get_with_default', 'not_in_doc'),
                                   ('Lists', 'get', 'argument'),
                                   ('Dict', 'insert', 'value'),
                                   ('Dict', 'update', 'value'))
        return client.ClientGenerator('Client', self.params['_resource_package'], _host, verification_exceptions=verification_exceptions).code

    @hammock.get('_api')
    def get_api(self):
        return doc.generate(self.params['_resource_package'])
