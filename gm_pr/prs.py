from gm_pr import models
from celery import group
from gm_pr.celery import app

import json, urllib.request

def get_json(url) :
    """ get json data from url.
    Auth is managed in __init__.py in this module
    """
    response = urllib.request.urlopen(url)
    charset = response.info().get_content_charset()
    if charset == None:
        charset = 'utf-8'
    string = response.read().decode(charset)
    return json.loads(string)

@app.task
def fetch_data(project_name, url, org):
    """ Celery task, call github api
    """
    pr_list = []
    project = { 'name' : project_name,
                'pr_list' : pr_list,
    }
    url = "%s/repos/%s/%s/pulls" % (url, org, project_name)
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


class Prs:
    def __init__(self, url, org, projects):
        self.__url = url
        self.__org = org
        self.__projects = projects

    def get_prs(self):
        """
        fetch the prs from github

        return a list of { 'name' : project_name, 'pr_list' : pr_list }
        pr_list is a list of models.Pr
        """
        res = group(fetch_data.s(project_name, self.__url, self.__org) for project_name in self.__projects)()
        data = res.get()
        return [ project for project in data if project != None ]
