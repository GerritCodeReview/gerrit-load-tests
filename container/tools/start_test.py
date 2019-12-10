#!/usr/bin/python3

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

import argparse
import logging
import os
import random
import time

import numpy as np

import actions
import config

LOG_PATH = "/var/logs/loadtester.log"


class LoadTestInstance:
    def __init__(self, test_config):
        self.config = test_config
        self.log = logging.getLogger("ActionLogger")

        if self.config["testrun"]["initialization"]["delay"]["enabled"]:
            self._wait_random_seconds(
                self.config["testrun"]["initialization"]["delay"]["min"],
                self.config["testrun"]["initialization"]["delay"]["max"],
            )

        self.url = self.config["gerrit"]["url"]
        self.user = self.config["gerrit"]["user"]
        self.pwd = self.config["gerrit"]["password"]

        self.timeout = (
            time.time() + self.config["testrun"]["duration"]
            if self.config["testrun"]["duration"]
            else None
        )

        self.action_config = self.config["actions"]

        self.owned_projects = set()
        if self.config["testrun"]["initialization"]["knownProjects"]:
            self.owned_projects = set(
                self.config["testrun"]["initialization"]["knownProjects"]
            )

        self.cloned_projects = set()

        if self.config["testrun"]["initialization"]["createProjects"]["enabled"]:
            self._create_initial_projects(
                self.config["testrun"]["initialization"]["createProjects"]["number"]
            )

    def run(self):
        while True:
            if self.timeout and time.time() >= self.timeout:
                break

            if self.config["testrun"]["waitBetweenCycles"]["enabled"]:
                self._wait_random_seconds(
                    self.config["testrun"]["waitBetweenCycles"]["min"],
                    self.config["testrun"]["waitBetweenCycles"]["max"],
                )

            self._exec_create_project_action()
            self._exec_list_projects_action()

            if self.owned_projects:
                self._exec_clone_project_action()

            if self.cloned_projects:
                self._exec_fetch_project_action()
                self._exec_push_head_to_master_action()
                self._exec_push_change_action()

            self._exec_query_hundred_open_changes_action()
            self._exec_review_change_action()

    def _create_initial_projects(self, num_init_projects):
        for _ in range(num_init_projects):
            self.owned_projects.add(
                actions.CreateProjectAction(
                    self.url, self.user, self.pwd, 1.0
                ).execute()
            )

    def _wait_random_seconds(self, min_wait, max_wait):
        wait_duration = random.randint(min_wait, max_wait)
        self.log.info("Waiting for %d seconds.", wait_duration)
        time.sleep(wait_duration)

    @staticmethod
    def _choose_from_list_poisson(input_list):
        probabilities = np.random.poisson(20, len(input_list))
        probabilities = probabilities / np.sum(probabilities)
        return np.random.choice(input_list, 1, p=probabilities).tolist()[0]

    def _exec_create_project_action(self):
        action = actions.CreateProjectAction(
            self.url,
            self.user,
            self.pwd,
            self.action_config["create_project"]["probability"],
        )
        project_name = action.execute()
        if not action.failed and project_name:
            self.owned_projects.add(project_name)

    def _exec_list_projects_action(self):
        action = actions.QueryProjectsAction(
            self.url,
            self.user,
            self.pwd,
            self.action_config["query_projects"]["probability"],
        )
        project_name = action.execute()
        if not action.failed and project_name:
            self.owned_projects.add(project_name)

    def _exec_clone_project_action(self):
        action = actions.CloneProjectAction(
            self.url,
            self.user,
            self.pwd,
            self._choose_from_list_poisson(list(self.owned_projects)),
            self.action_config["clone_project"]["probability"],
        )
        action.execute()
        if not action.failed and action.was_executed:
            self.cloned_projects.add(action.project_name)

    def _exec_fetch_project_action(self):
        action = actions.FetchProjectAction(
            self._choose_from_list_poisson(list(self.cloned_projects)),
            self.action_config["fetch_project"]["probability"],
        )
        action.execute()

    def _exec_push_head_to_master_action(self):
        action = actions.PushHeadToMasterAction(
            self._choose_from_list_poisson(list(self.cloned_projects)),
            self.action_config["push_head_to_master"]["probability"],
        )
        action.execute()

    def _exec_push_change_action(self):
        action = actions.PushForReviewAction(
            self._choose_from_list_poisson(list(self.cloned_projects)),
            self.action_config["push_for_review"]["probability"],
        )
        action.execute()

    def _exec_query_hundred_open_changes_action(self):
        action = actions.QueryHundredOpenChanges(
            self.url,
            self.user,
            self.pwd,
            self.action_config["query_hundred_open_changes"]["probability"],
        )
        action.execute()

    def _exec_review_change_action(self):
        action = actions.ReviewChangeAction(
            self.url,
            self.user,
            self.pwd,
            self.action_config["review_change"]["probability"],
        )
        action.execute()


# pylint: disable=C0103
if __name__ == "__main__":

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    log_format = "%(asctime)s %(message)s"

    logging.basicConfig(
        level=logging.DEBUG, format=log_format, filename=LOG_PATH, filemode="w"
    )

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger("ActionLogger").addHandler(handler)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-U", "--url", help="Gerrit base url", dest="url", action="store"
    )

    parser.add_argument("-u", "--user", help="Gerrit user", dest="user", action="store")

    parser.add_argument(
        "-p", "--password", help="Gerrit password", dest="password", action="store"
    )

    parser.add_argument(
        "-d",
        "--duration",
        help="Test duration in seconds",
        dest="duration",
        action="store",
        type=int,
    )

    parser.add_argument(
        "-c", "--config", help="Configuration file", dest="config_file", action="store"
    )

    args = parser.parse_args()

    test = LoadTestInstance(config.Parser(args).parse())
    test.run()
