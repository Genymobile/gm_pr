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

from gm_pr import models, paginablejson, settings, practivity
from celery import group, subtask
from gm_pr.celery import app
from operator import attrgetter
from django.utils import dateparse
from django.utils import timezone

import re
import logging

logger = logging.getLogger('gm_pr')

class PullRequest:
    """ Simple class wrapper for PullRequest properties
    """
    def __init__(self, url="", title="", updated_at="", user="", my_open_comment_count=0, last_activity=None,
                 repo="", nbreview=0, feedback_ok=0, feedback_weak=0,
                 feedback_ko=0, milestone=None, labels=None,
                 is_old=False):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.my_open_comment_count = my_open_comment_count
        self.last_activity = last_activity
        self.repo = repo
        self.nbreview = nbreview
        self.feedback_ok = feedback_ok
        self.feedback_weak = feedback_weak
        self.feedback_ko = feedback_ko
        self.milestone = milestone
        self.labels = labels
        self.is_old = is_old

def is_color_light(rgb_hex_color_string):
    """ return true if the given html hex color string is a "light" color
    https://en.wikipedia.org/wiki/Relative_luminance
    """
    r, g, b = rgb_hex_color_string[:2], rgb_hex_color_string[2:4], \
              rgb_hex_color_string[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    y = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

    return y > 128

def parse_githubdata(data, current_user):
    """
    data { 'repo': genymotion-libauth,
           detail: paginable,
           label: paginable,
           json: json,
           comment: paginable, (optional)
           review_comments: paginable, (optional)
           events: paginable, (optional)
           commits: paginable, (optional)
         }
    return Pr
    """

    now = timezone.now()
    feedback_ok = 0
    feedback_weak = 0
    feedback_ko = 0
    milestone = data['json']['milestone']
    labels = list()
    last_event = None
    last_commit = None

    if 'events' in data: last_event = practivity.get_latest_event(data['events'])
    if 'commits' in data: last_commit = practivity.get_latest_commit(data['commits'])
    last_activity = practivity.get_latest_activity(last_event, last_commit)

    for lbl in data['label']:
        label_style = 'light' if is_color_light(lbl['color']) else 'dark'
        labels.append({'name' : lbl['name'],
                       'color' : lbl['color'],
                       'style' : label_style,
        })

    date = dateparse.parse_datetime(data['json']['updated_at'])
    is_old = False
    if (now - date).days >= settings.OLD_PERIOD:
        if not labels and None in settings.OLD_LABELS:
            is_old = True
        else:
            for lbl in labels:
                if lbl['name'] in settings.OLD_LABELS:
                    is_old = True
                    break

    if current_user is not None:
        my_open_comment_count = get_open_comment_count(data['review_comments'], current_user)
    else:
        my_open_comment_count = 0

    # look for tags and activity only in main conversation and not in "file changed"
    if "comments" in settings.LAST_ACTIVITY_FILTER:
        for jcomment in data['comment']:
            body = jcomment['body']
            comment_activity = practivity.PrActivity(jcomment['updated_at'],
                                                     jcomment['user']['login'],
                                                     "commented")
            last_activity = practivity.get_latest_activity(last_activity, comment_activity)

    if milestone:
        milestone = milestone['title']

    try:
        pr = PullRequest(url=data['json']['html_url'],
                         title=data['json']['title'],
                         updated_at=date,
                         user=data['json']['user']['login'],
                         my_open_comment_count=my_open_comment_count,
                         last_activity=last_activity,
                         repo=data['json']['base']['repo']['name'],
                         nbreview=int(data['detail']['comments']) +
                                  int(data['detail']['review_comments']),
                         feedback_ok=feedback_ok,
                         feedback_weak=feedback_weak,
                         feedback_ko=feedback_ko,
                         milestone=milestone,
                         labels=labels,
                         is_old=is_old)
    except Exception as e:
        logger.error("cannot create PullRequest: %s", e)

    return pr

@app.task
def get_urls_for_repo(repo_name, url, org, current_user):
    """ get all "suburl" (comments, labels, detail, ...) from the "pulls" url
    for a repo.
    return a list of "tagurl" hash. Each tagurl element represent an url with
    meta data (type, repoid)
    """
    url = "%s/repos/%s/%s/pulls" % (url, org, repo_name)
    json_prlist = paginablejson.PaginableJson(url)
    tagurls = []
    if not json_prlist:
        return tagurls
    for json_pr in json_prlist:
        if json_pr['state'] == 'open':
            tagurls.append({ 'repo' : repo_name,
                             'tag' : 'json',
                             'prid' : json_pr['id'],
                             # XXX: this is not a url. We pass the json to have
                             # it in the final data response.
                             # see get_tagdata_from_tagurl
                             'url' : json_pr })
            if "comments" in settings.LAST_ACTIVITY_FILTER:
                tagurls.append({ 'repo' : repo_name,
                                 'tag' : 'comment',
                                 'prid' : json_pr['id'],
                                 'url' : json_pr['comments_url'] })
            tagurls.append({ 'repo' : repo_name,
                             'tag' : 'detail',
                             'prid' : json_pr['id'],
                             'url' : json_pr['url'] })
            tagurls.append({ 'repo' : repo_name,
                             'tag' : 'label',
                             'prid' : json_pr['id'],
                             'url' : "%s/labels" % json_pr['issue_url'] })
            if current_user:
                tagurls.append({ 'repo' : repo_name,
                                 'tag' : 'review_comments',
                                 'prid' : json_pr['id'],
                                 'url' : json_pr['review_comments_url'] })
            if "events" in settings.LAST_ACTIVITY_FILTER:
                tagurls.append({ 'repo' : repo_name,
                                 'tag' : 'events',
                                 'prid' : json_pr['id'],
                                 'url' : "%s/events" % json_pr['issue_url'] })
            if "commits" in settings.LAST_ACTIVITY_FILTER:
                tagurls.append({ 'repo' : repo_name,
                                 'tag' : 'commits',
                                 'prid' : json_pr['id'],
                                 'url' : json_pr['commits_url'] })
    return tagurls

@app.task
def dmap(it, callback):
    # http://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    return group(callback.clone((arg,)) for arg in it)()


@app.task
def get_tagdata_from_tagurl(tagurl):
    """ Transform a tagurl to a tagdata: do the HTTP request
    """
    if tagurl['tag'] == 'json':
        return { 'repo' : tagurl['repo'],
                 'tag' : tagurl['tag'],
                 'prid' : tagurl['prid'],
                 'json' : tagurl['url']}
    else:
        return { 'repo' : tagurl['repo'],
                 'tag' : tagurl['tag'],
                 'prid' : tagurl['prid'],
                 'json' : paginablejson.PaginableJson(tagurl['url'])}


# Return the number of non-obsolete review comments posted on the given PR url, by the given user.
def get_open_comment_count(review_comments, user):
    open_comment_count=0
    for review_comment in review_comments:
        # In obsolote comments, the position is None
        if review_comment['position'] is not None and review_comment['user']['login'] == user:
            open_comment_count +=1
    return open_comment_count


class PrFetcher:
    """ Pr fetcher
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
        pr_list is a list of Pr
        """
        # { 41343736 : { 'repo': genymotion-libauth,
        #                detail: paginable,
        #                label: paginable,
        #                comment: paginable } }
        github_data = {}
        # Parallelisation strategy: get_urls_for_repo will extract every urls
        # needed for every open PR on a repo. Those urls are stored in a hash
        # with metadata to identify where do they come from (tagurl).
        # Each tagurl is distributed to a celery worker to do the HTTP request
        # and retrieve the data (tagdata). The data is a PaginableJson.
        # Then we merge all the tagdata from the same PR (same prid) and parse
        # the result. The merge and parsing is done by django
        # FIXME: In the parsing function (parse_githubdata), we iterate
        # on a PaginableJson. This can result in a http request (if there
        # is more than one page). In this case the request will be done in the
        # django process (not the celery worker) and will not be parallelised
        res = group((get_urls_for_repo.s(repo.name, self.__url, self.__org,
                                         self.__current_user) | \
                     dmap.s(get_tagdata_from_tagurl.s()))
                    for repo in self.__repos)()
        data = res.get()
        for groupres in res.get():
            for tagdata in groupres.get():
                prid = tagdata['prid']
                if prid not in github_data:
                    github_data[prid] = {}
                    github_data[prid]['repo'] = tagdata['repo']
                github_data[prid][tagdata['tag']] = tagdata['json']

        prlist = [ parse_githubdata(github_data[prid], self.__current_user)
                   for prid in github_data ]
        repo_pr = {}
        for pr in prlist:
            if pr.repo not in repo_pr:
                repo_pr[pr.repo] = []
            repo_pr[pr.repo].append(pr)

        return repo_pr
