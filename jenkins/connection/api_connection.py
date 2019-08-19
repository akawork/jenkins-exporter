import requests
from requests.auth import HTTPBasicAuth


class APIConnection(object):

    def __init__(self, server, auth, insecure=True):
        self.session = requests.Session()
        self.server = server
        self.auth = auth
        self.verify = insecure

    def do_get(self, url, params=None):
        response = self.session.get(
            url=url,
            params=params,
            auth=self.auth,
            verify=self.verify
        )
        return response

    def do_post(self, url, params=None):
        self.session.post(
            url=url,
            params=params,
            auth=self.auth,
            verify=self.verify
        )
