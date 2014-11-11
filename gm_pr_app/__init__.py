import urllib.request
from gm_pr_app import settings

import base64

#http://stackoverflow.com/questions/2407126/python-urllib2-basic-auth-problem
class PreemptiveBasicAuthHandler(urllib.request.HTTPBasicAuthHandler):
    '''Preemptive basic auth.

    Instead of waiting for a 403 to then retry with the credentials,
    send the credentials if the url is handled by the password manager.
    Note: please use realm=None when calling add_password.'''
    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        # this is very similar to the code from retry_http_basic_auth()
        # but returns a request object.
        user, pw = self.passwd.find_user_password(realm, url)
        if pw:
            raw = "%s:%s" % (user, pw)
            auth = "Basic %s" % (base64.b64encode(raw.encode()).strip()).decode()
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request


# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

password_mgr.add_password(None, settings.TOP_LEVEL_URL,
                          settings.GITHUB_LOGIN, settings.GITHUB_PASSWORD)

handler = PreemptiveBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# Install the opener.
# Now all calls to urllib.request.urlopen use our opener.
urllib.request.install_opener(opener)
