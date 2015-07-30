FROM debian:jessie
RUN apt-get update
RUN apt-get install -y python3-django python3-django-celery celeryd python3-sqlalchemy supervisor apache2 libapache2-mod-wsgi-py3
ADD gm_pr.conf /etc/apache2/sites-available/gm_pr.conf
RUN a2ensite gm_pr
EXPOSE 80
WORKDIR /var/www/gm_pr
CMD chown -R www-data:www-data . && supervisord -c deploy/supervisord.conf
