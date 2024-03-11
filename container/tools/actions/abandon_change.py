# Copyright (C) 2024 The Android Open Source Project
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

import requests

from . import abstract
from .query_hundred_open_changes import QueryHundredOpenChanges


class AbandonChangeAction(abstract.AbstractAction):
    def __init__(self, url, user, pwd, probability=1):
        super().__init__(url, user, pwd, probability)
        self.change_id = None

    def _execute_action(self):
        self.change_id = self._get_change_id()
        rest_url = self._assemble_abandon_url()
        requests.post(rest_url, auth=(self.user, self.pwd))
        self.was_executed = True

    def _create_log_message(self):
        return self.change_id

    def _get_change_id(self):
        try:
            return QueryHundredOpenChanges(
                self.url, self.user, self.pwd, 1.0
            ).execute()["change_id"]
        except Exception:
            return None

    def _assemble_abandon_url(self):
        return "%s/a/changes/%s/abandon" % (
            self.url,
            self.change_id,
        )
