#
# Copyright 2019 Genymobile
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
from gm_pr.models import Project, Repo, default_columns
from gm_pr import settings

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Initialize admin user, projects and repos"

    def add_arguments(self, parser):
        parser.add_argument("projects", nargs="*",
                            help="project definition, using the form: "
                                 "$project=$repo1,$repo2")

    def handle(self, *args, **options):
        self.create_admin_user()
        for project in settings.INITIAL_PROJECTS.split(";"):
            self.create_project(project)
        for project in options['projects']:
            self.create_project(project)

    def create_admin_user(self):
        try:
            User.objects.create_superuser(
                settings.ADMIN_LOGIN, settings.ADMIN_EMAIL,
                settings.ADMIN_PASSWORD)
        except IntegrityError:
            self.stdout.write("admin user already created")

    def create_project(self, project_str):
        project_name, repos_str = project_str.split("=")

        self.stdout.write("Creating project {}".format(project_name))
        project, created = Project.objects.get_or_create(name=project_name)
        if created:
            # Django cannot set columns until the project instance exists, so
            # save now
            project.save()
            project.columns = default_columns()
            project.save()
        else:
            self.stdout.write("Project already exists")

        for repo_name in repos_str.split(","):
            self.stdout.write("Adding repo {} to {}".format(repo_name,
                                                            project_name))
            repo, _ = Repo.objects.get_or_create(name=repo_name)
            repo.projects.add(project)
            repo.save()
