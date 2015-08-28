#
# Copyright 2015 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import json
import urllib.request
from gm_pr.prfetcher import PrFetcher
from gm_pr.celery import app
from gm_pr import settings

@app.task
def slack(url, org, weburl, repos, slackurl, channel):
    """ Celery task, use github api and send result to slack
    """
    prf = PrFetcher(url, org, repos, None)
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

    urllib.request.urlopen(slackurl, json.dumps(payload).encode('utf-8'))
