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

from django.db import models
from django.core.exceptions import ValidationError


class Project(models.Model):
    """ Project: group of many github repo
    """
    name = models.CharField(max_length=256)

    def clean(self):
        if Project.objects.filter(name=self.name).exists():
            raise ValidationError('Project %s already exists' % self.name)

    def __eq__(self, other):
        return self.name == other

    def __str__(self):
        return self.name


class Repo(models.Model):
    """ Repo: github repo
    """
    name = models.CharField(max_length=256)
    projects = models.ManyToManyField(Project)

    def clean(self):
        if Repo.objects.filter(name=self.name).exists():
            raise ValidationError('Repo %s already exists' % self.name)

    def __eq__(self, other):
        return self.name == other

    def __str__(self):
        return self.name
