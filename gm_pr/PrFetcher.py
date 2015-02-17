from gm_pr import models, PaginableJson, settings
from celery import group
from gm_pr.celery import app

import re
from datetime import datetime

@app.task
def fetch_data(project_name, url, org):
    """ Celery task, call github api
    """
    pr_list = []
    project = {'name' : project_name,
               'pr_list' : pr_list,
              }
    url = "%s/repos/%s/%s/pulls" % (url, org, project_name)
    jdata = PaginableJson.PaginableJson(url)
    now = datetime.now()
    if not jdata:
        return
    for jpr in jdata:
        if jpr['state'] == 'open':
            detail_json = PaginableJson.PaginableJson(jpr['url'])
            comment_json = PaginableJson.PaginableJson(detail_json['comments_url'])
            plusone = 0
            lgtm = 0
            milestone = jpr['milestone']
            label_json = PaginableJson.PaginableJson(jpr['issue_url'] + '/labels')
            labels = list()
            if label_json:
                for lbl in label_json:
                    labels.append({'name' : lbl['name'],
                                   'color' : lbl['color'],
                               })

            date = datetime.strptime(detail_json['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            is_old = False
            if (now - date).days >= settings.OLD_PERIOD:
                if not labels and None in settings.OLD_LABELS:
                    is_old = True
                else:
                    for lbl in labels:
                        if lbl['name'] in settings.OLD_LABELS:
                            is_old = True
                            break

            # look for tags only in main conversion and not in "file changed"
            for jcomment in comment_json:
                body = jcomment['body']
                if re.search(":\+1:", body):
                    plusone += 1
                if re.search("LGTM", body, re.IGNORECASE):
                    lgtm += 1
            if milestone:
                milestone = milestone['title']
            pr = models.Pr(url=jpr['html_url'],
                           title=jpr['title'],
                           updated_at=jpr['updated_at'],
                           user=jpr['user']['login'],
                           repo=jpr['base']['repo']['full_name'],
                           nbreview=int(detail_json['comments']) + \
                                    int(detail_json['review_comments']),
                           plusone=plusone,
                           lgtm=lgtm,
                           milestone=milestone,
                           labels=labels,
                           is_old=is_old)
            pr_list.append(pr)

    sorted(pr_list, key=lambda pr: pr.updated_at)

    if not pr_list:
        return None
    return project


class PrFetcher:
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
        res = group(fetch_data.s(project_name, self.__url, self.__org)
                    for project_name in self.__projects)()
        data = res.get()
        return [project for project in data if project != None]
