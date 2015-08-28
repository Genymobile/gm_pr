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

from gm_pr import models, paginablejson, settings
from celery import group
from gm_pr.celery import app
from operator import attrgetter
from django.utils import dateparse
from django.utils import timezone

import re

def is_color_light(rgb_hex_color_string):
    """ return true if the given html hex color string is a "light" color
    https://en.wikipedia.org/wiki/Relative_luminance
    """
    r, g, b = rgb_hex_color_string[:2], rgb_hex_color_string[2:4], \
              rgb_hex_color_string[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    y = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

    return y > 128

@app.task
def fetch_data(repo_name, url, org, current_user):
    """ Celery task, call github api
    repo_name -- github repo name
    url -- base url for this repo
    org -- github organisation

    return a dict {'name' : repo_name, 'pr_list' : pr_list} with pr_list a list
    of models.Pr
    """
    pr_list = []
    repo = {'name' : repo_name,
            'pr_list' : pr_list,
           }
    url = "%s/repos/%s/%s/pulls" % (url, org, repo_name)
    json_prlist = paginablejson.PaginableJson(url)
    now = timezone.now()
    if not json_prlist:
        return
    for json_pr in json_prlist:
        if json_pr['state'] == 'open':
            conversation_json = paginablejson.PaginableJson(json_pr['comments_url'])
            detail_json = paginablejson.PaginableJson(json_pr['url'])
            feedback_ok = 0
            feedback_weak = 0
            feedback_ko = 0
            milestone = json_pr['milestone']
            label_json = paginablejson.PaginableJson("%s/labels" % \
                                                     json_pr['issue_url'])
            labels = list()
            if label_json:
                for lbl in label_json:
                    label_style = 'light' if is_color_light(lbl['color']) else 'dark'
                    labels.append({'name' : lbl['name'],
                                   'color' : lbl['color'],
                                   'style' : label_style,
                                  })

            date = dateparse.parse_datetime(json_pr['updated_at'])
            is_old = False
            if (now - date).days >= settings.OLD_PERIOD:
                if not labels and None in settings.OLD_LABELS:
                    is_old = True
                else:
                    for lbl in labels:
                        if lbl['name'] in settings.OLD_LABELS:
                            is_old = True
                            break

            # look for tags only in main conversation and not in "file changed"
            if current_user is not None:
                my_open_comment_count = get_open_comment_count(json_pr['review_comments_url'], current_user)
            else:
                my_open_comment_count = 0
            for jcomment in conversation_json:
                body = jcomment['body']
                if re.search(settings.FEEDBACK_OK['keyword'], body):
                    feedback_ok += 1
                if re.search(settings.FEEDBACK_WEAK['keyword'], body):
                    feedback_weak += 1
                if re.search(settings.FEEDBACK_KO['keyword'], body):
                    feedback_ko += 1
            if milestone:
                milestone = milestone['title']

            pr = models.Pr(url=json_pr['html_url'],
                           title=json_pr['title'],
                           updated_at=date,
                           user=json_pr['user']['login'],
                           my_open_comment_count=my_open_comment_count,
                           repo=json_pr['base']['repo']['full_name'],
                           nbreview=int(detail_json['comments']) +
                                    int(detail_json['review_comments']),
                           feedback_ok=feedback_ok,
                           feedback_weak=feedback_weak,
                           feedback_ko=feedback_ko,
                           milestone=milestone,
                           labels=labels,
                           is_old=is_old)
            pr_list.append(pr)

    repo['pr_list'] = sorted(pr_list, key=attrgetter('updated_at'), reverse=True)

    if not pr_list:
        return None

    return repo

# Return the number of non-obsolete review comments posted on the given PR url, by the given user.
def get_open_comment_count(url, user):
    open_comment_count=0
    review_comments = paginablejson.PaginableJson(url)
    for review_comment in review_comments:
        # In obsolote comments, the position is None
        if review_comment['position'] is not None and review_comment['user']['login'] == user:
            open_comment_count +=1
    return open_comment_count


class PrFetcher:
    """ Pr fetc
    """
    def __init__(self, url, org, repos, current_user):
        """
        url -- top level url (eg: https://api.github.com)
        org -- github organisation (eg: Genymobile)
        repos -- repo name (eg: gm_pr)
        """
        self.__url = url
        self.__org = org
        self.__repos = repos
        self.__current_user = current_user

    def get_prs(self):
        """
        fetch the prs from github

        return a list of { 'name' : repo_name, 'pr_list' : pr_list }
        pr_list is a list of models.Pr
        """
        res = group(fetch_data.s(repo_name, self.__url, self.__org, self.__current_user)
                    for repo_name in self.__repos)()
        data = res.get()
        return [repo for repo in data if repo != None]
