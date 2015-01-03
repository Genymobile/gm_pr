from django.conf.urls import patterns, url

from bot import views

urlpatterns = patterns('',
                       url(r'^.*$', views.index, name='index'),
                      )
