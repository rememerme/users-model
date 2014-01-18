import requests
from rememerme.users.models import User

class UserClientError(Exception):
    pass

def strip_trailing_slash(url):
    if url[-1] == '/':
        return url[:-1]
    return url

class UserClient:
    DEFAULT_URL = 'http://134.53.148.103'

    def __init__(self, session_id, url=DEFAULT_URL):
        self.url = strip_trailing_slash(url)
        self.session_id = session_id

    def create(self, username, password):
        return NotImplementedError()
        payload = { 'username':username, 'password':password }
        r = requests.post(self.url + '/rest/v1/sessions',data=payload)
        if r.status_code is not 200:
            raise UserClientError(r.text)
        return User.fromMap(r.json())

    def update(self, user_id, username=None, password=None, email=None):
        payload = {}
        if username: payload['username'] = username
        if password: payload['password'] = password
        if email: payload['email'] = email
        
        headers = { 'HTTP_AUTHORIZATION' : self.session_id }
        
        r = requests.put(self.url + '/rest/v1/sessions/%s' % str(user_id), data=payload, headers=headers)
        if r.status_code is not 200:
            raise UserClientError(r.text)
        return User.fromMap(r.json())
    
    def get(self, user_id):
        headers = { 'HTTP_AUTHORIZATION' : self.session_id }
        r = requests.delete(self.url + '/rest/v1/sessions/%s' % str(user_id), headers=headers)
        if r.status_code is not 200:
            raise UserClientError(r.text)
        return User.fromMap(r.json())
