import urllib.request
import json
from gm_pr import settings
from gm_pr import models

from celery import group
from gm_pr.celery import app

def __get_json(url) :
    response = urllib.request.urlopen(url)
    charset = response.info().get_content_charset()
    if charset == None:
        charset = 'utf-8'
    string = response.read().decode(charset)
    return json.loads(string)

@app.task
def __fetch_data(project_name):
    pr_list = []
    project = { 'name' : project_name,
                'pr_list' : pr_list,
            }
    url = "%s/repos/%s/%s/pulls" % (settings.TOP_LEVEL_URL,
                                    settings.ORG,
                                    project_name)
    jdata = __get_json(url)
    if len(jdata) == 0:
        return
    for jpr in jdata:
        if jpr['state'] == 'open':
            comment_json = __get_json(jpr['comments_url'])
            review_json = __get_json(jpr['review_comments_url'])

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

def get_prs():
    """
    fetch the prs from github

    return a list of { 'name' : project_name, 'pr_list' : pr_list }
    pr_list is a list of models.Pr
    """
    res = group(__fetch_data.s(project_name) for project_name in settings.PROJECTS)()
    data = res.get()
    return [ project for project in data if project != None ]
