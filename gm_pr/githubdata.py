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

from gm_pr import practivity, settings
from gm_pr.pullrequest import PullRequest
from gm_pr.tag import Tag
from django.utils import timezone, dateparse

logger = logging.getLogger('gm_pr')


class GithubFragmentUrl:
    """Url found in a json provided by the Github API
    fetch_githubfragmenturl is in charge of fetching this url in a celery task.
    Once fetched, it become a GithubFragment
    """
    def __init__(self, repo, tag, prid, url):
        self.repo = repo
        self.tag = tag
        self.prid = prid
        self.url = url

    def __str__(self):
        return "repo:%s tag:%s id:%s url:%s" % \
            (self.repo, self.tag.name, self.prid, self.url)

class GithubFragment:
    """ Piece of data contained provided by the Github API
    """
    def __init__(self, repo, tag, prid, data):
        self.repo = repo
        self.tag = tag
        self.prid = prid
        self.data = data

    def __str__(self):
        return "repo:%s tag:%s id:%s data:%s" % \
            (self.repo, self.tag.name, self.prid, self.data)


def is_color_light(rgb_hex_color_string):
    """ return true if the given html hex color string is a "light" color
    https://en.wikipedia.org/wiki/Relative_luminance
    """
    r, g, b = rgb_hex_color_string[:2], rgb_hex_color_string[2:4], \
              rgb_hex_color_string[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    y = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

    return y > 128

def get_open_comment_count(review_comments, user):
    """ Return the number of non-obsolete review comments posted on the given
        PR url, by the given user."""
    return sum(1 for review_comment in review_comments
               # In obsolote comments, the position is None
               if review_comment['position'] and
               review_comment['user']['login'] == user)

class GithubPr:
    """ This class map a PR in Github, all data are fetched.
    """
    def __init__(self, prid):
        self.__prid = prid
        self.__details = None
        self.__labels = None
        self.__info = None
        self.__comments = None
        self.__reviews = None
        self.__review_comments = None
        self.__events = None
        self.__commits = None

    def addfragment(self, fragment):
        """ A Github PR is made of piece of data contains in several url (GithubFragment)
        To construct a full PR, you need to call this method with all the fragments
        """
        assert fragment.prid == self.__prid
        if fragment.tag == Tag.DETAILS:
            self.__details = fragment.data
        elif fragment.tag == Tag.LABELS:
            self.__labels = fragment.data
        elif fragment.tag == Tag.INFO:
            self.__info = fragment.data
        elif fragment.tag == Tag.COMMENTS:
            self.__comments = fragment.data
        elif fragment.tag == Tag.REVIEWS:
            self.__reviews = fragment.data
        elif fragment.tag == Tag.REVIEW_COMMENTS:
            self.__review_comments = fragment.data
        elif fragment.tag == Tag.EVENTS:
            self.__events = fragment.data
        elif fragment.tag == Tag.COMMITS:
            self.__commits = fragment.data
        else:
            raise Exception("unknown tag")


    def parsepr(self, current_user):
        """ Parse the data and return a _pr.pullrequest.PullRequest
        """
        assert self.__info is not None, "need to call addfragment on id %s" % self.__prid
        assert self.__details is not None, "need to call addfragment on id %s" % self.__prid
        assert self.__labels is not None, "need to call addfragment on id %s" % self.__prid
        assert self.__reviews is not None, "need to call addfragment on id %s" % self.__prid

        now = timezone.now()
        feedback_ok = 0
        feedback_ko = 0
        milestone = self.__info['milestone']
        labels = list()
        last_event = None
        last_commit = None
        targetbranch = None

        if self.__events:
            last_event = practivity.get_latest_event(self.__events)
        if self.__commits:
            last_commit = practivity.get_latest_commit(self.__commits)
        last_activity = practivity.get_latest_activity(last_event, last_commit)

        for lbl in self.__labels:
            label_style = 'light' if is_color_light(lbl['color']) else 'dark'
            labels.append({'name' : lbl['name'],
                           'color' : lbl['color'],
                           'style' : label_style,
            })

        date = dateparse.parse_datetime(self.__info['updated_at'])
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
            my_open_comment_count = get_open_comment_count(self.__review_comments,
                                                           current_user)
        else:
            my_open_comment_count = 0

        # look for tags and activity only in main conversation and not in "file changed"
        if "comments" in settings.LAST_ACTIVITY_FILTER:
            for comment in self.__comments:
                comment_activity = practivity.PrActivity(comment['updated_at'],
                                                         comment['user']['login'],
                                                         "commented")
                last_activity = practivity.get_latest_activity(last_activity, comment_activity)

        review_by_user = {}
        for review in self.__reviews:
            login = review['user']['login']
            # only last review matter. Assume reviews are ordered and take only the last review
            # for each user, ignoring COMMENTED
            if review['state'] == "CHANGES_REQUESTED" or review['state'] == "APPROVED":
                review_by_user[login] = review['state']

            if "reviews" in settings.LAST_ACTIVITY_FILTER:
                review_activity = practivity.PrActivity(review['submitted_at'],
                                                        login,
                                                        "reviewed")
                last_activity = practivity.get_latest_activity(last_activity, review_activity)

        feedback_ok = sum(1 for k, v in review_by_user.items() if v == "APPROVED")
        feedback_ko = sum(1 for k, v in review_by_user.items() if v == "CHANGES_REQUESTED")

        if milestone:
            milestone = milestone['title']

        pr = PullRequest(url=self.__info['html_url'],
                         title=self.__info['title'],
                         updated_at=date,
                         user=self.__info['user']['login'],
                         my_open_comment_count=my_open_comment_count,
                         last_activity=last_activity,
                         repo=self.__info['base']['repo']['name'],
                         nbreview=int(self.__details['comments']) +
                                  int(self.__details['review_comments']),
                         feedback_ok=feedback_ok,
                         feedback_ko=feedback_ko,
                         milestone=milestone,
                         labels=labels,
                         is_old=is_old,
                         targetbranch=self.__info['base']['ref'],
        )

        return pr
