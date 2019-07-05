import requests
from requests.auth import HTTPBasicAuth

class HttpRequests:

    def __init__(self, collector):
        self._session = requests.Session()
        self._collector = collector
        self._auth = (self._collector._user, self._collector._passwd)
        self._verify = (not self._collector._insecure)
        

    def getHttpResponse(self, my_url): 
        response = self._session.get(my_url, auth=self._auth, verify = (self._verify))
        
        #Connection fail
        if response.status_code != 200:
            print('******************************************************************************************')
            print('  Connection fail: ')
            print('   - Status code: {}'.format(response.status_code))
            print('   - Url: {}'.format(my_url))
            print('   - Username: {}'.format(self._collector._user))
            print('   - Password: {}'.format(self._collector._passwd))
            print('******************************************************************************************')

        return response
