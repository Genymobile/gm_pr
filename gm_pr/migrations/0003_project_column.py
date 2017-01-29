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

from __future__ import unicode_literals

from django.db import migrations, models
import gm_pr.models

# don't use settings_projects.py or the migration may fail if DEFAULT_COLUMNS get
# changed
CURRENT_DEFAULT_COLUMNS = [ "lastupdate",
                            "lastactivity",
                            "labels",
                            "title",
                            "user",
                            "reviews",
                            "opencomments",
                            "approved",
                            "reqchanges",
                          ]
def default_columns(app):
    Column = app.get_model("gm_pr", "Column")
    columns = []
    for column in CURRENT_DEFAULT_COLUMNS:
        columns.append(Column.objects.get(name=column))

    return columns


def setcolumn(app, schema_editor):
    Project = app.get_model("gm_pr", "Project")
    for project in Project.objects.all():
        if not project.columns.all():
            for column in default_columns(app):
                project.columns.add(column.pk)
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('gm_pr', '0002_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='columns',
            field=models.ManyToManyField(to='gm_pr.Column', default=gm_pr.models.default_columns),
        ),
        migrations.RunPython(setcolumn)
    ]
