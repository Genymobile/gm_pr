from gm_pr import models, PaginableJson, settings
from celery import group
from gm_pr.celery import app
from operator import attrgetter

import re
from datetime import datetime


# return true if the given html hex color string is a "light" color
def is_color_light(rgb_hex_color_string):
    r, g, b = rgb_hex_color_string[:2], rgb_hex_color_string[2:4], rgb_hex_color_string[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    # https://en.wikipedia.org/wiki/Relative_luminance
    y = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
    return (y > 128)

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
            feedback_ok = 0
            feedback_weak = 0
            feedback_ko = 0
            milestone = jpr['milestone']
            label_json = PaginableJson.PaginableJson(jpr['issue_url'] + '/labels')
            labels = list()
            if label_json:
                for lbl in label_json:
                    label_style = 'light' if is_color_light(lbl['color']) else 'dark'
                    labels.append({'name' : lbl['name'],
                                   'color' : lbl['color'],
                                   'style' : label_style
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
                if re.search(settings.FEEDBACK_OK['keyword'], body):
                    feedback_ok += 1
                if re.search(settings.FEEDBACK_WEAK['keyword'], body):
                    feedback_weak += 1
                if re.search(settings.FEEDBACK_KO['keyword'], body):
                    feedback_ko += 1
            if milestone:
                milestone = milestone['title']
            pr = models.Pr(url=jpr['html_url'],
                           title=jpr['title'],
                           updated_at=date,
                           user=jpr['user']['login'],
                           repo=jpr['base']['repo']['full_name'],
                           nbreview=int(detail_json['comments']) + \
                                    int(detail_json['review_comments']),
                           feedback_ok=feedback_ok,
                           feedback_weak=feedback_weak,
                           feedback_ko=feedback_ko,
                           milestone=milestone,
                           labels=labels,
                           is_old=is_old)
            pr_list.append(pr)

    project['pr_list'] = sorted(pr_list, key=attrgetter('updated_at'), reverse=True)

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
