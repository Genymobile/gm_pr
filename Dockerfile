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

FROM debian:jessie
RUN apt-get update
RUN apt-get install -y \
    celeryd \
    rabbitmq-server \
    supervisor \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3-pip
COPY deploy/commons.txt /tmp/commons.txt
RUN pip3 install -r /tmp/commons.txt
COPY deploy/gm_pr.conf /etc/apache2/sites-available/gm_pr.conf
RUN a2ensite gm_pr

EXPOSE 80
COPY . /var/www/gm_pr
WORKDIR /var/www/gm_pr
CMD chown -R www-data:www-data . && supervisord -c deploy/supervisord.conf
