# Create your views here.


from django.http import HttpResponse
from django.shortcuts import render
from gm_pr_app import settings
from gm_pr_app import models
import urllib.request
import json
from multiprocessing import pool

def get_json(url) :
    response = urllib.request.urlopen(url)
    charset = response.info().get_content_charset()
    if charset == None:
        charset = 'utf-8'
    string = response.read().decode(charset)
    return json.loads(string)


def fetch_data(project_name):
    pr_list = []
    project = { 'name' : project_name,
                'pr_list' : pr_list,
            }
    url = "%s/repos/%s/%s/pulls" % (settings.TOP_LEVEL_URL,
                                    settings.ORG,
                                    project_name)
    jdata = get_json(url)
    if len(jdata) == 0:
        return
    for jpr in jdata:
        if jpr['state'] == 'open':
            comment_json = get_json(jpr['comments_url'])
            review_json = get_json(jpr['review_comments_url'])

            pr = models.Pr(url = jpr['html_url'],
                           title = jpr['title'],
                           updated_at = jpr['updated_at'],
                           user = jpr['user']['login'],
                           repo = jpr['base']['repo']['full_name'],
                           nbreview = len(review_json) + len(comment_json))
            pr_list.append(pr)

    sorted(pr_list, key=lambda pr: pr.updated_at)

    if len(pr_list) == 0:
        return None
    return project

import time

def index(request):
    before = time.time()
    project_list = []
    p = pool.Pool(20)
    context = { "project_list" : project_list }

    workers = []
    for project_name in settings.PROJECTS:
        worker = p.apply_async(fetch_data, (project_name,))
        workers.append(worker)

    p.close()
    p.join()
    for worker in workers:
        proj = worker.get()
        if proj:
            project_list.append(proj)

    after = time.time()
    print(after - before)
    return render(request, 'pr.html', context)
