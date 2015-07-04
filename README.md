Multi project Github PullRequest integration for Slack
======================================================

Slack setup:
  * Add a "Incomming webhook" and copy the url in gm_pr.settings.SLACK_URL
  the channel do not matter as it will be overrided in the script

  * Add a "Slash command"
    * use the GET method
    * the url is where you deployed this django app followed by "/bot"
    * copy the token in gm_pr.settings.SLACK_TOKEN

Script setup
  * Configure the slack channel / projects list mapping in gm_pr.settings.PROJECTS_CHAN

  * Configure the github login / password

  * WEB_URL is where you deployed this django app

Docker cmd:
  something like:

    docker run --name=gm_pr -d -p 4280:8000 -v /var/www/gm_pr:/var/www/gm_pr gm_pr


Manual instructions:
====================

Prerequisites (MacOS/homebrew):
-------------------------------
```
brew doctor
brew update

brew install python3
pip3 install django
pip3 install django-celery
```

Configuring the web page only:
------------------------------

Edit gm_pr/settings.py.
Set the following:

* GITHUB_LOGIN
* GITHUB_PASSWORD
* ORG
* PROJECTS_CHAN

Run the following commands to start the server:
```
python3 manage.py migrate
python3 manage.py runserver 192.168.1.4:8000
```

Run the following command in a new terminal:
```
celery -A gm_pr worker -l info --concurrency=20
```


Open the web page at http://192.168.1.4:8000

