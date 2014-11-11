from django.conf.urls import patterns, url

from gm_pr_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
