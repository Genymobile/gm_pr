# Create your views here.


from django.http import HttpResponse
from django.shortcuts import render
from gm_pr_app import settings
from gm_pr_app import models
import urllib.request
import json
from multiprocessing import pool


def fetch_data(project_name):
    pr_list = []
    project = { 'name' : project_name,
                'pr_list' : pr_list,
            }
    url = "%s/repos/%s/%s/pulls" % (settings.TOP_LEVEL_URL,
                                    settings.ORG,
                                    project_name)
    response = urllib.request.urlopen(url)
    charset = response.info().get_content_charset()
    if charset == None:
        charset = 'utf-8'
    string = response.read().decode(charset)
    jdata = json.loads(string)
    if len(jdata) == 0:
        return
    for jpr in jdata:
        if jpr['state'] == 'open':
            pr = models.Pr(url = jpr['html_url'],
                           title = jpr['title'],
                           updated_at = jpr['updated_at'],
                           user = jpr['user']['login'],
                           repo = jpr['base']['repo']['full_name'])
            pr_list.append(pr)

    sorted(pr_list, key=lambda pr: pr.updated_at)

    return project


def index(request):
    project_list = []
    p = pool.Pool(10)
    context = { "project_list" : project_list }

    workers = []
    for project_name in settings.PROJECTS:
        worker = p.apply_async(fetch_data, (project_name,))
        workers.append(worker)

    p.close()
    p.join()
    for worker in workers:
        project_list.append(worker.get())

    return render(request, 'pr.html', context)
