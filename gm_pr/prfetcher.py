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

import logging

from gm_pr import paginablejson, settings
from gm_pr.githubdata import GithubPr, GithubFragmentUrl, GithubFragment
from gm_pr.tag import Tag
from gm_pr.celery import app
from celery import group, subtask

logger = logging.getLogger('gm_pr')

@app.task
def get_fragments_for_repo(repo_name, url, org, current_user):
    """ get all GithubFragmentUrl (comments, labels, detail, ...) from the "pulls" url
    for a repo.
    """
    url = "%s/repos/%s/%s/pulls" % (url, org, repo_name)
    json_prlist = paginablejson.PaginableJson(url)
    fragments = []
    if not json_prlist:
        return fragments
    for json_pr in json_prlist:
        if json_pr['state'] == 'open':
            prid = json_pr['id']
            fragments.append(GithubFragment(repo_name, Tag.INFO, prid, json_pr))

            if "comments" in settings.LAST_ACTIVITY_FILTER:
                fragments.append(GithubFragmentUrl(repo_name, Tag.COMMENTS,
                                                   prid, json_pr['comments_url']))

            fragments.append(GithubFragmentUrl(repo_name, Tag.DETAILS,
                                               prid, json_pr['url']))
            fragments.append(GithubFragmentUrl(repo_name, Tag.LABELS,
                                               prid, "%s/labels" % json_pr['issue_url']))

            fragments.append(GithubFragmentUrl(repo_name, Tag.REVIEWS,
                                               prid, "%s/reviews" % json_pr['url']))

            if current_user:
                fragments.append(GithubFragmentUrl(repo_name, Tag.REVIEW_COMMENTS,
                                                   prid, json_pr['review_comments_url']))
            if "events" in settings.LAST_ACTIVITY_FILTER:
                fragments.append(GithubFragmentUrl(repo_name, Tag.EVENTS,
                                                   prid, "%s/events" % json_pr['issue_url']))
            if "commits" in settings.LAST_ACTIVITY_FILTER:
                fragments.append(GithubFragmentUrl(repo_name, Tag.COMMITS,
                                                   prid, json_pr['commits_url']))

    return fragments

@app.task
def dmap(it, callback):
    # http://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    return group(callback.clone((arg,)) for arg in it)()


@app.task
def fetch_githubfragmenturl(githubfragment):
    """ githubfragment can be a GithubFragment or a GithubFragmentUrl

    in case of GithubFragmentUrl we do a HTTP request """
    if isinstance(githubfragment, GithubFragment):
        return githubfragment
    else:
        return GithubFragment(githubfragment.repo,
                              githubfragment.tag,
                              githubfragment.prid,
                              paginablejson.PaginableJson(githubfragment.url))


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
        pr_list is a list of PullRequest
        """
        # Parallelisation strategy: get_fragments_for_repo will extract every urls
        # needed for every open PR on a repo. Those urls are stored in a GithubFragmentUrl
        # Each GithubFragmentUrl is distributed to a celery worker to do the HTTP request
        # and retrieve the data (GithubFragment).
        # Then we merge (addfragment) all the GithubFragment from the same PR (same prid)
        # and parse the result. The merge and parsing is done by django
        res = group((get_fragments_for_repo.s(repo.name, self.__url, self.__org,
                                              self.__current_user) | \
                     dmap.s(fetch_githubfragmenturl.s()))
                    for repo in self.__repos)()

        githubpr_by_id = {}
        for groupres in res.get():
            for fragment in groupres.get():
                prid = fragment.prid
                if prid not in githubpr_by_id:
                    githubpr_by_id[prid] = GithubPr(prid)
                githubpr_by_id[prid].addfragment(fragment)

        prlist = [githubPr.parsepr(self.__current_user) for githubPr in githubpr_by_id.values()]

        repo_pr = {}
        for pullrequest in prlist:
            if pullrequest.repo not in repo_pr:
                repo_pr[pullrequest.repo] = []
            repo_pr[pullrequest.repo].append(pullrequest)

        return repo_pr
