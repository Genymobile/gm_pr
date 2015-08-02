# gm_pr configuration

##
# Github configuration
##

# generate a token here: https://github.com/settings/tokens
GITHUB_OAUTHTOKEN = "xxxx"
# name of your github organisation
ORG = "Genymobile"
# do not change this :-)
TOP_LEVEL_URL = "https://api.github.com"

##
# Slack configuration (ignore this section if do not use slack)
##

# link to the web version
WEB_URL = "http://www.example.org/gm_pr/"
SLACK_TOKEN = "xxx"
SLACK_URL = "https://hooks.slack.com/services/xxxx"

##
# Project configuration
##

# Number of days a PRs without update can be flagged as OLD.
OLD_PERIOD = 4
# only PRs with one of those labels can be considered as OLD.
# Use None for "no label"
OLD_LABELS = ("Needs Reviews", None)

# gm_pr will parse the "conversation" related to each PR to count those symbols
# The count is available in the web page and can be used to know if your peers
# agree to merge this PR or not
# keyword is the text to search for in the github comments, name is the web
# page column heading
FEEDBACK_OK = {"keyword": "LGTM", "name" : "LGTM"}
FEEDBACK_WEAK = {"keyword" : ":hand:", "name" : "&#9995;"}
FEEDBACK_KO = {"keyword": ":x:", "name" :"&#10007;"}

# list of repo associated with each projects.
# Here "opensource" is the name of a project (you're free to choose the name you
# want) and 'genymotion-binocle', 'FridgeCheckup' and 'gm_pr' are github's
# repo name
# Note for slack user: The name of the project (eg: opensource) must match the
# name of the slack channel
PROJECTS_REPOS = \
    {'opensource' : ('genymotion-binocle',
                      'FridgeCheckup',
                      'gm_pr',
                    ),
     'test' : ('test',
                )
    }
