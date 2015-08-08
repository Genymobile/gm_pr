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

import json, urllib.request

class PaginableJson:
    """ fetch json data with automatic pagination
    Auth is managed in __init__.py in this module
    """
    def __fetch_data(self, url):
        self.__idx = 0
        if self.__end:
            raise StopIteration
        if self.__last_url == url:
            self.__end = True

        response = urllib.request.urlopen(url)
        charset = response.info().get_content_charset()
        if charset == None:
            charset = 'utf-8'

        if 'Link' in response.info():
            #pagination
            for infopage in response.info()['Link'].split(','):
                if infopage.split(';')[1].strip() == 'rel="next"':
                    self.__next_url = infopage.split(';')[0].strip()
                if infopage.split(';')[1].strip() == 'rel="last"':
                    # overrided at each call...
                    self.__last_url = infopage.split(';')[0].strip()

        else:
            #no pagination
            self.__next_url = None

        self.__data = json.loads(response.read().decode(charset))

    def __retrieve_data(self):
        data = self.__data
        idx = self.__idx
        if self.__idx >= len(self.__data) - 1:
            self.__data = None
        self.__idx += 1
        return data[idx]


    def __init__(self, url):
        self.__url = url
        self.__next_url = None
        self.__last_url = None
        self.__data = None
        self.__idx = 0
        self.__end = False
        # need to get data now, len is called before iteration
        self.__fetch_data(url)


    def __iter__(self):
        return self

    def __next__(self):
        # current batch not yet exausted or first call
        if self.__data:
            return self.__retrieve_data()

        # not paginable
        if not self.__next_url:
            raise StopIteration

        self.__fetch_data(self.__next_url)
        return self.__retrieve_data()

    def __len__(self):
        return len(self.__data)


    def __getitem__(self, key):
        return self.__data[key]
