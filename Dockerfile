FROM 32bit/debian:jessie
RUN apt-get update
RUN apt-get install -y python3-django python3-django-celery celeryd python3-sqlalchemy supervisor
RUN useradd -u 1000 -m gmpr
EXPOSE 8080
USER gmpr
WORKDIR /var/www/gm_pr
CMD supervisord
