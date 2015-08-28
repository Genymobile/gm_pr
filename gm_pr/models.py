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

class Pr:
    """ Simple class wrapper for pr properties
    """
    def __init__(self, url="", title="", updated_at="", user="", my_open_comment_count=0,
                 repo="", nbreview=0, feedback_ok=0, feedback_weak=0,
                 feedback_ko=0, milestone=None, labels=None,
                 is_old=False):
        self.url = url
        self.title = title
        self.updated_at = updated_at
        self.user = user
        self.my_open_comment_count = my_open_comment_count
        self.repo = repo
        self.nbreview = nbreview
        self.feedback_ok = feedback_ok
        self.feedback_weak = feedback_weak
        self.feedback_ko = feedback_ko
        self.milestone = milestone
        self.labels = labels
        self.is_old = is_old
