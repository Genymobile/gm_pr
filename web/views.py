# Create your views here.


from django.shortcuts import render
from django.http import HttpResponse
from gm_pr import settings, chan_proj
from gm_pr.PrFetcher import PrFetcher
import time

def index(request):
    if not request.GET :
        context = {'title': "Project list", 'project_list' : settings.PROJECTS_CHAN.keys()}
        return render(request, 'index.html', context)

    projects, channel = chan_proj.chan_proj(request)

    if projects != None:
        before = time.time()

        prf = PrFetcher(settings.TOP_LEVEL_URL, settings.ORG, projects)
        context = {"title" : channel + " PR list", "project_list" : prf.get_prs(),
                   "feedback_ok" : settings.FEEDBACK_OK['name'],
                   "feedback_weak" : settings.FEEDBACK_WEAK['name'],
                   "feedback_ko" : settings.FEEDBACK_KO['name']}

        after = time.time()
        print(after - before)
        return render(request, 'pr.html', context)
    else:
        return HttpResponse("No projects found\n", status=404)
