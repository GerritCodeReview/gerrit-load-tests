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

import yaml

DEFAULTS = {
    "gerrit": {"url": None, "user": "admin", "password": "secret"},
    "testrun": {"duration": None},
    "actions": {
        "clone_project": {"probability": 1},
        "create_project": {"probability": 1},
        "fetch_project": {"probability": 1},
        "push_for_review": {"probability": 1},
        "push_to_branch": {"probability": 1},
        "query_changes": {"probability": 1},
        "query_projects": {"probability": 1},
        "review_change": {"probability": 1},
    },
}

ARG_TO_CONFIG_MAPPING = {
    "url": {"category": "gerrit", "option": "url"},
    "user": {"category": "gerrit", "option": "user"},
    "password": {"category": "gerrit", "option": "password"},
    "duration": {"category": "testrun", "option": "duration"},
}


class Parser:
    def __init__(self, args):
        self.args = vars(args)

        self.config = DEFAULTS

    def parse(self):
        if self.args["config_file"]:
            for category, category_dict in self._parse_config_file().items():
                for option, value in category_dict.items():
                    self.config[category][option] = value

        self._apply_args()

        return self.config

    def _apply_args(self):
        for arg, arg_mapping in ARG_TO_CONFIG_MAPPING.items():
            if self.args[arg]:
                self.config[arg_mapping["category"]][arg_mapping["option"]] = self.args[
                    arg
                ]

    def _parse_config_file(self):
        if not os.path.exists(self.args["config_file"]):
            raise FileNotFoundError(
                "Could not find config file: %s" % self.args["config_file"]
            )

        with open(self.args["config_file"], "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
