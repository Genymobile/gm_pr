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

from gm_pr import settings

def proj_repo(request):
    """ Retrieve project list from a Slack request or web request.
    Parameter come from GET and can be either 'channel_name' or 'project' (they
    both give the same result)
    return a tuple: list of projects, channel name
    """
    repos = None
    project = None
    if request.GET != None and \
       'channel_name' in request.GET or 'project' in request.GET:
        if 'channel_name' in request.GET:
            project = request.GET['channel_name']
        else:
            project = request.GET['project']

        if project in settings.PROJECTS_REPOS:
            repos = settings.PROJECTS_REPOS[project]
    return project, repos
