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
from django.http import HttpResponse

def isFromSlack(function):
    def __wrap(request, *args, **kwargs):
        if request.GET != None and 'token' in request.GET \
           and request.GET['token'] == settings.SLACK_TOKEN:
            return function(request, *args, **kwargs)
        else:
            return HttpResponse("Forbidden\n", status=403)

    return __wrap
