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

import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger('gm_pr')

class PaginableJson:
    """ fetch json data and follow pagination
    Auth is managed in __init__.py in this module
    If the request returns a list of json, this class is iterable and like a
    list of json dictionnary.
    Otherwise it behave like a dictionnary
    """
    def __init__(self, url):
        self.__url = url
        self.__data = []
        self.__fetch_data()

    def __get_page(self, url):
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            logger.warning("cannot open %s: %s", url, e.reason)
            return (None, [])

        charset = response.info().get_content_charset()
        if not charset:
            charset = 'utf-8'
        return (response, json.loads(response.read().decode(charset)))


    def __fetch_data(self):
        last_url = None
        url = self.__url

        (response, data) = self.__get_page(url)
        if not response:
            return

        if 'Link' not in response.info():
            self.__data = data
        else:
            self.__data.extend(data)
            while True:
                for infopage in response.info()['Link'].split(','):
                    if infopage.split(';')[1].strip() == 'rel="next"':
                        url = infopage.split(';')[0].strip()
                    if infopage.split(';')[1].strip() == 'rel="last"':
                        # overrided at each iter...
                        last_url = infopage.split(';')[0].strip()

                (response, data) = self.__get_page(url)
                if not response:
                    break

                self.__data.extend(data)

                if url == last_url or "page=0" in last_url:
                    break


    def get_last(self):
        return self.__data[-1]

    def __iter__(self):
        return self.__data.__iter__()

    def __len__(self):
        return len(self.__data)

    def __getitem__(self, key):
        return self.__data[key]

    def __str__(self):
        return "PaginableJson %s" % str(self.__data)
