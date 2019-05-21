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

import os

# The settings in this file may be modified directly
# in this file, or set with environment variables.
# The environment variables are the same name as the
# settings named, prefixed by GM_PR_.
# Example, the environment variable GM_PR_GITHUB_OAUTHTOKEN
# can be used instead of setting GITHUB_OAUTHTOKEN directly
# in this file.


def _read_str(key, fallback=None, mandatory=False):
    env_key = "GM_PR_{}".format(key)
    try:
        return os.environ[env_key]
    except KeyError:
        if mandatory:
            raise Exception("Mandatory key '{}' not set".format(env_key))
        else:
            return fallback


def _read_int(key, fallback=None, mandatory=False):
    str_value = _read_str(key, mandatory=mandatory)
    return fallback if str_value is None else int(str_value)


def _read_tuple(key, fallback=None, mandatory=False):
    str_value = _read_str(key, mandatory=mandatory)
    return fallback if str_value is None else str_value.split(",")


##
# Github configuration
##

# generate a token here: https://github.com/settings/tokens
GITHUB_OAUTHTOKEN = _read_str('GITHUB_OAUTHTOKEN')
# name of your github organisation
ORG = _read_str('ORG', 'Genymobile')
# do not change this :-)
TOP_LEVEL_URL = "https://api.github.com"

# Activities to include in the "Last Activity" column.
# Possible values are:
# "reviews"
# "comments" (slower page loading due to extra request)
# "events" (slower page loading due to extra request)
# "commits" (slower page loading due to extra request)
#LAST_ACTIVITY_FILTER = ("comments", "events", "commits") #slower but provides more information
#LAST_ACTIVITY_FILTER = ("comments") # faster but less information.
#Ex: env GM_PR_LAST_ACTIVITY_FILTER="comments,events,commits"
LAST_ACTIVITY_FILTER = _read_tuple("LAST_ACTIVITY_FILTER",
                                   ("reviews", "comments"))


DEFAULT_COLUMNS = _read_tuple("DEFAULT_COLUMNS",
                              ("lastupdate", "lastactivity", "labels", "title",
                               "user", "reviews", "opencomments", "approved",
                               "reqchanges", "targetbranch"))

##
# Slack configuration (ignore this section if you do not use slack)
##

# link to the web version
WEB_URL = _read_str('WEB_URL', 'https://gmpr.example.org')
# slack authentification token
SLACK_TOKEN = _read_str('SLACK_TOKEN')
# incoming-webhook url
SLACK_URL = _read_str('SLACK_URL')

##
# Project configuration
##

# Number of days a PRs without update can be flagged as OLD.
OLD_PERIOD = _read_int("OLD_PERIOD", 4)
# only PRs with one of those labels can be considered as OLD.
# Use None for "no label"
OLD_LABELS = ("Needs Reviews", None)

ADMIN_LOGIN = _read_str("ADMIN_LOGIN", "admin")
ADMIN_EMAIL = _read_str("ADMIN_EMAIL", "admin@localhost")
ADMIN_PASSWORD = _read_str("ADMIN_PASSWORD", "admin")

INITIAL_PROJECTS = _read_str("INITIAL_PROJECTS")
