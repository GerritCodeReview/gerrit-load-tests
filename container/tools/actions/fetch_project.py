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

import os.path

import git

from . import abstract

# pylint: disable=W0703


class FetchProjectAction(abstract.AbstractAction):
    def __init__(self, project_name, probability=1):
        super().__init__(url=None, user=None, pwd=None, probability=probability)
        self.project_name = project_name

    def _execute_action(self):
        local_repo_path = os.path.join("/tmp", self.project_name)
        if os.path.exists(local_repo_path):
            repo = git.Repo(local_repo_path)
            for remote in repo.remotes:
                remote.fetch()
            self.was_executed = True

    def _create_log_message(self):
        return self.project_name
