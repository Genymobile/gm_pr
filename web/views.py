# Create your views here.


from django.shortcuts import render
from django.http import HttpResponse
from gm_pr import settings, proj_repo
from gm_pr.prfetcher import PrFetcher
import time

def index(request):
    if not request.GET:
        context = {'title': "Project list",
                   'project_list' : settings.PROJECTS_REPOS.keys()}
        return render(request, 'index.html', context)

    project, repos = proj_repo.proj_repo(request)

    if repos != None:
        before = time.time()

        prf = PrFetcher(settings.TOP_LEVEL_URL, settings.ORG, repos)
        context = {"title" : "%s PR list" % project,
                   "project_list" : prf.get_prs(),
                   "feedback_ok" : settings.FEEDBACK_OK['name'],
                   "feedback_weak" : settings.FEEDBACK_WEAK['name'],
                   "feedback_ko" : settings.FEEDBACK_KO['name']}

        after = time.time()
        print(after - before)
        return render(request, 'pr.html', context)
    else:
        return HttpResponse("No projects found\n", status=404)
