# Django settings for gm_pr projects.

import os

GITHUB_OAUTHTOKEN="xxxx"
#web version
WEB_URL = "http://www.example.org/gm_pr/"
SLACK_TOKEN = "xxx"
SLACK_URL = "https://hooks.slack.com/services/xxxx"

TOP_LEVEL_URL = "https://api.github.com"
ORG = "Genymobile"
# Number of days a PRs without update can be flagged as OLD.
OLD_PERIOD=4
# only PRs with one of those labels can be considered as OLD.
# Use None for "no label"
OLD_LABELS=("Needs Reviews", None)

PROJECTS_CHAN = \
    { 'general' : ("genymotion-binocle",
                  ),
      'random' : ('FridgeCheckup',
                 ),
    }
