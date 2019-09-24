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

import copy


def left_outer_join(dict_a, dict_b):
    merged_dict = copy.deepcopy(dict_a)
    merged_dict = _recursive_left_outer_join(merged_dict, dict_b)

    return merged_dict


def _recursive_left_outer_join(dict_a, dict_b):
    for key, value in dict_a.items():
        if key not in dict_b:
            continue
        if isinstance(value, dict):
            if not isinstance(dict_b[key], dict):
                raise ValueError("Expected dictionary as value of key '%s'" % key)
            dict_a[key] = _recursive_left_outer_join(value, dict_b[key])
        else:
            dict_a[key] = dict_b[key]

    return dict_a
