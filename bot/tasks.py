from __future__ import absolute_import

import json
import urllib.request
from gm_pr.PrFetcher import PrFetcher
from gm_pr.celery import app

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
                txt += "<%s|%s> %s review:%d LGTM:%d :+1::%d\n" % (pr.url, pr.title, pr.user, pr.nbreview, pr.lgtm, pr.plusone)


    payload = {"channel": channel,
               "username": "genypr",
               "text": txt,
               "icon_emoji": ":Y:"}

    urllib.request.urlopen(slack, json.dumps(payload).encode('utf-8'))
