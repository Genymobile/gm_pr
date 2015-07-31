from __future__ import absolute_import

import json
import urllib.request
from gm_pr.PrFetcher import PrFetcher
from gm_pr.celery import app
from gm_pr import settings

@app.task
def slack(url, org, weburl, project, slack, channel):
    """ Celery task, use github api and send result to slack
    """
    prf = PrFetcher(url, org, project)
    project_list = prf.get_prs()
    nb_proj = len(project_list)
    total_pr = 0
    for proj in project_list:
        nb_pr = len(proj['pr_list'])
        total_pr += nb_pr

    txt = """Hey, we have %d PR in %d project(s) (<%s|web version>)
""" % (total_pr, nb_proj, weburl)

    if total_pr > 0:
        txt += "\n"
        for proj in project_list:
            txt += "*%s*\n" % proj['name']
            for pr in proj['pr_list']:
                txt += "<%s|%s> -" % (pr.url, pr.title)
                if pr.milestone:
                    txt += " *%s* -" % (pr.milestone)
                for label in pr.labels:
                    txt += " *%s* -" % (label['name'])
                txt += " %s review:%d %s:%d %s:%d %s:%d\n" % \
                       (pr.user, pr.nbreview,
                        settings.FEEDBACK_OK['keyword'], pr.feedback_ok,
                        settings.FEEDBACK_WEAK['keyword'], pr.feedback_weak,
                        settings.FEEDBACK_KO['keyword'], pr.feedback_ko)


    payload = {"channel": channel,
               "username": "genypr",
               "text": txt,
               "icon_emoji": ":y:"}

    urllib.request.urlopen(slack, json.dumps(payload).encode('utf-8'))
