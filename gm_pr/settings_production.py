# Django settings for gm_pr project, production environment.
from gm_pr.settings import *

DEBUG = False
TEMPLATE_DEBUG = False

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [ "127.0.0.1"]

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = 'http://example.com/static/'

