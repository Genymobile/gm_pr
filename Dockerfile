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

FROM ubuntu:18.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apache2 \
        libapache2-mod-wsgi-py3 \
        python3-celery \
        python3-pip \
        rabbitmq-server \
        supervisor

COPY requirements/commons.txt /tmp/commons.txt
RUN pip3 install -r /tmp/commons.txt
COPY deploy/gm_pr.conf /etc/apache2/sites-available/gm_pr.conf
RUN a2ensite gm_pr
RUN mkdir /var/run/apache2

EXPOSE 80
COPY . /var/www/gm_pr
WORKDIR /var/www/gm_pr
RUN mkdir rw

# Run this before chowning rw because it creates rw/gm_pr.log as root
# Define dummy values for mandatory settings otherwise python can't import
# settings.py
RUN GM_PR_GITHUB_OAUTHTOKEN=dummy GM_PR_ORG=dummy python3 manage.py collectstatic --noinput

RUN chown -R www-data:www-data rw
CMD supervisord -c deploy/supervisord.conf
