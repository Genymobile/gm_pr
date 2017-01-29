# gm_pr: A multi project Github pull request viewer


If your project is spread over multiple git repositories, it can be hard to
keep track of all the open pull requests.

The gm_pr project gives you a simple web page where you can see all the open
pull requests with the number of reviews, labels, milestones, etc

![screenshot](screenshot.png)

As a bonus, we also have a slack bot :-)

## Installation

The recommended method to run gm_pr is to use the docker image.

A [Dockerfile](Dockerfile) is available. Building and running the image
can be done in a few lines:

```
docker build -t gm_pr .
docker volume create --name gmpr
# mount the volume in /var/www/gm_pr/rw for log and sqlite db
docker run -v gmpr:/var/www/gm_pr/rw -e GM_PR_ORG=MyOrg -e GM_PR_GITHUB_OAUTHTOKEN=xxxx -e GM_PR_ADMIN_LOGIN="admin" -e GM_PR_ADMIN_PASSWORD="admin" --name gm_pr -p 8000:80 -d gm_pr
```

 * GM_PR_ORG: Your Github organisation
 * GM_PR_GITHUB_OAUTHTOKEN: oauth token for your github account, see https://github.com/settings/tokens
 * GM_PR_ADMIN_LOGIN and GM_PR_ADMIN_PASSWORD configure a login/password for gm_pr administration

Now, you can simply point your browser to http://localhost:8000.

## Configuration

The prefered way to configure gm_pr is to set environment variables for docker.
Alternatively, you can modify 2 files:

 * gm_pr/settings.py: this is the standard Django configuration file
 * gm_pr/settings_projects.py: configure your Github and Slack organization and authentication here.

### Django configuration

Refer to the django project if you want to change the configuration.
Normally you should only need to adjust a few settings:

**ALLOWED_HOSTS** list the hosts allowed to connect to this app.
Use "*" to allow everything.
This is the first thing to check if you see a "Bad Request (400)"
This parameter is configurable with environment variable `GM_PR_ALLOWED_HOSTS`

**STATIC_URL** Add the full URL to your static directory

### Gm_pr configuration

Open **gm_pr/settings_projects.py** and read the comments. You should be able
to customize your installation by setting environment variables.

### add projects

To add projects, visit the "admin/" page. Add a *project* then add all the
related github *repo*s

You can also have some inital projects when starting docker with the environment
variable `GM_PR_INITIAL_PROJECTS`

eg: `GM_PR_INITIAL_PROJECTS="Material design repos=material-design-lite,material-design-icons;GCM repos=gcm,go-gcm"`

### Slack configuration

You can see your pull requests from Slack.

You need to add a "slash command" in the slack settings:

 * Open https://my.slack.com/services/new/slash-commands
 * Choose a command name, for eg: "/pr"
 * For the URL, append "/bot/" to your gm_pr URL.
 * In order to make things easy with the Django CSRF protection, you have to
 choose the GET method.
 * Copy the token and add it in **settings_project.py** (**SLACK_TOKEN**)
 * click on "Save Integration"

Then you need to add a incoming-webhook to let the bot send messages to Slack:

 * Open https://my.slack.com/services/new/incoming-webhook
 * Choose a channel (the bot will be able to override it, so it doesn't really
 matter what you enter)
 * Copy the webhook URL in **setting_project.py** (**SLACK_URL**)

Now, go to the channel related to your project and type "/pr". After a
few seconds the list of pull requests should appear in your channel.

### Environment variables

 * `GM_PR_ALLOWED_HOSTS`: list of host allowed to connect on the app (default "*")
 * `GM_PR_GITHUB_OAUTHTOKEN`: github oauth token
 * `GM_PR_ORG`: github organisation
 * `GM_PR_LAST_ACTIVITY_FILTER`: Info in the activity column (see settings_project.py)
 * `GM_PR_WEB_URL`: used by slackbot, link to the web version
 * `GM_PR_SLACK_TOKEN`: slack token
 * `GM_PR_SLACK_URL`: slack hook url
 * `GM_PR_OLD_PERIOD`: number of days before a PR is marked as old
 * `GM_PR_ADMIN_LOGIN`: django admin login
 * `GM_PR_ADMIN_EMAL`: django admin email
 * `GM_PR_ADMIN_PASSWORD`: django admin password
 * `GM_PR_INITIAL_PROJECTS`: comma separated initial project "project1=repo1,repo2;project2=repo3"
 * `GM_PR_DEFAULT_COLUMNS`: comma separated list of column to display (see settings_project.py)

## Hacking

You need to install django for python3, celery and rabbitmq

Here is the command line for MacOS/homebrew

```
brew doctor
brew update

brew install python3 rabbitmq-server
pip3 install -r requirements/commons.txt
```

On Debian-like system

```
sudo apt-get install python3 celeryd rabbitmq-server
sudo pip3 install -r requirements/commons.txt
```

Create a user and vhost for rabbitmq

```
sudo rabbitmqctl add_user gm_pr gm_pr
sudo rabbitmqctl add_vhost gm_pr
sudo rabbitmqctl set_permissions -p gm_pr gm_pr ".*" ".*" ".*"

```

Run the following commands to start the server:
```
python3 manage.py migrate
env GM_PR_ORG=MyOrg GM_PR_ALLOWED_HOSTS="10.0.0.2,10.0.0.3" python3 manage.py runserver
```

Run the following command in a new terminal:
```
env GM_PR_GITHUB_OAUTHTOKEN=xxxx python3 manage.py celeryd
```

Open the web page at http://localhost:8000

# About gm_pr

Gm_pr is an open-source project distributed under the Apache license
version 2

If you like this project, click on the star button on github  :-)

Feel free to send us issues, and of course PRs!!
