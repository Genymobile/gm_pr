#
# Copyright 2016 Genymobile
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

# If the GM_PR_INITIAL_PROJECTS environment variable is set, this
# script will delete the database of projects and repos, and populate
# it based on the value of the environment variable.

# example environment variable value:
# env GM_PR_INITIAL_PROJECTS="Material design repos=material-design-lite,material-design-icons;GCM repos=gcm,go-gcm"

from gm_pr import models
import os

projects_str = os.environ.get("GM_PR_INITIAL_PROJECTS")
if projects_str:
    # We have an environment variable value, delete existing
    # projects and repos from the DB
    models.Project.objects.all().delete()
    models.Repo.objects.all().delete()
    projects = dict(item.split("=") for item in projects_str.split(";"))
    for project_name in projects:
        project = models.Project()
        project.name=project_name
        project.save()
        repo_list_str = projects[project_name]
        repo_list = repo_list_str.split(",")
        for repo_name in repo_list:
            repo = models.Repo()
            repo.name = repo_name
            # We need to save the repo before we link it
            # to the project, or else we'll get an error
            # "...needs to have a value for field...before this many-to-many relationship can be used"
            repo.save()
            repo.projects = [project]
            repo.save()

