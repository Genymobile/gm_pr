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

# Create your views here.


from django.shortcuts import render
from django.http import HttpResponse
from gm_pr import settings, proj_repo
from gm_pr.prfetcher import PrFetcher
import time

def index(request):
    if not request.GET:
        context = {'title': "Project list",
                   'project_list' : settings.PROJECTS_REPOS.keys()}
        return render(request, 'index.html', context)

    project, repos = proj_repo.proj_repo(request)

    if repos != None:
        before = time.time()

        current_user = None
        if 'login' in request.GET:
            current_user = request.GET['login']

        prf = PrFetcher(settings.TOP_LEVEL_URL, settings.ORG, repos, current_user)
        context = {"title" : "%s PR list" % project,
                   "project_list" : prf.get_prs(),
                   "feedback_ok" : settings.FEEDBACK_OK['name'],
                   "feedback_weak" : settings.FEEDBACK_WEAK['name'],
                   "feedback_ko" : settings.FEEDBACK_KO['name']}

        after = time.time()
        print(after - before)
        return render(request, 'pr.html', context)
    else:
        return HttpResponse("No projects found\n", status=404)
