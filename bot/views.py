from django.http import HttpResponse
from gm_pr import settings, chan_proj
from bot import tasks, slackAuth

@slackAuth.isFromSlack
def index(request):
    projects, channel_name = chan_proj.chan_proj(request)
    if projects != None:
        tasks.slack.delay(settings.TOP_LEVEL_URL, settings.ORG,
                          "%s?project=%s" % (settings.WEB_URL, channel_name),
                          projects,
                          settings.SLACK_URL,
                          "#%s" % channel_name)
        return HttpResponse("One moment, Octocat is considering your request\n")
    else:
        return HttpResponse("No project found\n", status=404)
