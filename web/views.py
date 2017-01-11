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
from gm_pr.models import Project, Repo
from gm_pr.prfetcher import PrFetcher
import time
import logging

logger = logging.getLogger('gm_pr')


def index(request):
    if not request.GET:
        context = {'title': "Project list",
                   'project_list' : Project.objects.order_by('name').all()}
        return render(request, 'index.html', context)

    project, repos = proj_repo.proj_repo(request)
    columns = Project.objects.get(name=project).columns.all()
    column_names = []
    for column in columns:
        column_names.append(column.name)

    if repos:
        before = time.time()

        current_user = None
        if 'login' in request.GET:
            current_user = request.GET['login']

        # We could optimize PrFetch by adjusting the number of request with the displayed columns.
        # However, this will make testing more difficult and code more complex.
        prf = PrFetcher(settings.TOP_LEVEL_URL, settings.ORG, repos, current_user)
        context = {"title" : project,
                   "projects" : prf.get_prs(),
                   "columns" : column_names}

        after = time.time()
        logger.debug("page generated in %s sec" % (after - before))
        return render(request, 'pr.html', context)
    else:
        return HttpResponse("No projects found\n", status=404)
