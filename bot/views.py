from django.http import HttpResponse
from gm_pr import settings, proj_repo
from bot import tasks, slackauth

@slackauth.isFromSlack
def index(request):
    project, repos = proj_repo.proj_repo(request)
    if repos != None:
        tasks.slack.delay(settings.TOP_LEVEL_URL,
                          settings.ORG,
                          "%s?project=%s" % (settings.WEB_URL, project),
                          repos,
                          settings.SLACK_URL,
                          "#%s" % project)
        return HttpResponse("One moment, Octocat is considering your request\n")
    else:
        return HttpResponse("No projects found\n", status=404)
