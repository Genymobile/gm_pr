FROM debian:jessie
RUN apt-get update
RUN apt-get install -y python3-django python3-django-celery celeryd python3-sqlalchemy supervisor
EXPOSE 8080
USER www-data
WORKDIR /var/www/gm_pr
CMD supervisord
