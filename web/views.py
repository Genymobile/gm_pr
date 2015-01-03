# Create your views here.


from django.shortcuts import render
from gm_pr import settings
from gm_pr.PrFetcher import PrFetcher
import time

def index(request):
    before = time.time()

    prf = PrFetcher(settings.TOP_LEVEL_URL, settings.ORG, settings.PROJECTS)
    context = {"project_list" : prf.get_prs()}

    after = time.time()
    print(after - before)
    return render(request, 'pr.html', context)
