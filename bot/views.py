from django.shortcuts import render
from django.http import HttpResponse

from bot import tasks

def index(request):
    res = tasks.slack.delay()
    return HttpResponse("One moment, Octocat is considering your request\n")
