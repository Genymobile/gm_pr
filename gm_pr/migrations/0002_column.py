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


class Migration(migrations.Migration):

    dependencies = [
        ('gm_pr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
        ),
        migrations.RunSQL(
            [("INSERT INTO gm_pr_column (name) VALUES ('lastupdate');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('lastactivity');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('milestone');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('labels');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('title');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('user');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('reviews');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('opencomments');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('approved');"),
             ("INSERT INTO gm_pr_column (name) VALUES ('reqchanges');"),
             ]
        ),
    ]
