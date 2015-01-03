# Create your views here.


from django.shortcuts import render
from gm_pr import prs
import time

def index(request):
    before = time.time()

    context = { "project_list" : prs.get_prs() }

    after = time.time()
    print(after - before)
    return render(request, 'pr.html', context)
