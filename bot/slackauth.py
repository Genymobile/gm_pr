from gm_pr import settings
from django.http import HttpResponse

def isFromSlack(function):
    def __wrap(request, *args, **kwargs):
        if request.GET != None and 'token' in request.GET \
           and request.GET['token'] == settings.SLACK_TOKEN:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse("Forbidden\n", status=403)

    return __wrap
