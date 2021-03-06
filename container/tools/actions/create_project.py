# Copyright (C) 2019 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import string

import requests

from . import abstract

PROJECT_NAME_LENGTH = 16


class CreateProjectAction(abstract.AbstractAction):
    def __init__(self, url, user, pwd, probability=1):
        super().__init__(url, user, pwd, probability)
        self.project_name = self._get_random_project_name()

    def _execute_action(self):
        rest_url = self._assemble_url()
        requests.put(
            rest_url, auth=(self.user, self.pwd), json={"create_empty_commit": "true"}
        )
        self.was_executed = True
        return self.project_name

    def _create_log_message(self):
        return self.project_name

    def _assemble_url(self):
        return "%s/a/projects/%s" % (self.url, self.project_name)

    @staticmethod
    def _get_random_project_name():
        allowed_symbols = string.ascii_letters + string.digits
        return "".join(
            [random.choice(allowed_symbols) for n in range(PROJECT_NAME_LENGTH)]
        )
