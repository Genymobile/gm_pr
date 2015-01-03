from __future__ import absolute_import

import json
import urllib.request
from gm_pr import prs
from gm_pr.celery import app

@app.task
def slack():
    project_list = prs.get_prs()
    nb_proj = len(project_list)
    total_pr = 0
    for proj in project_list:
        nb_pr = len(proj['pr_list'])
        total_pr += nb_pr

    txt="""Hey, we have %d PR in %d project(s) (<http://jenkins.genymobile.com|web version>)
""" % (total_pr, nb_proj)

    if total_pr > 0:
        txt += "\n"
        for proj in project_list:
            txt += "*%s*\n" % proj['name']
            for pr in proj['pr_list']:
                txt += "<%s|%s> %s %d\n" % (pr.url, pr.title, pr.user, pr.nbreview)


    payload = {"channel": "#general",
                "username": "webhookbot",
                "text": txt,
                "icon_emoji": ":oO:"}


    urllib.request.urlopen("https://hooks.slack.com/services/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", json.dumps(payload).encode('utf-8'))
