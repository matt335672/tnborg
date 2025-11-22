#!/usr/bin/python
#
# Copyright 2025 matt335672
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import configparser
import os
import subprocess
import sys


# --------------------------------------------------------------------------
# M A I N
# --------------------------------------------------------------------------

# Find the path to the config via the path to this file
dir = os.path.dirname(sys.argv[0])
dir, _ = os.path.split(dir)
dir = os.path.join(dir, "config")

# Read the config and configure the environment
config = configparser.ConfigParser()
config.read(os.path.join(dir, "config.ini"))
remote = config["global"]["rclone_remote"]

# Look for the section name we need in the creds file
env_key = remote + "-env"
creds = configparser.ConfigParser()
creds.read(os.path.join(dir, "creds.ini"))
if not env_key in creds:
    raise RuntimeError("Section '" + env_key + "' not in creds.ini")

# Set the creds up for rclone
for var in creds[env_key]:
    #print("Setting " + var.upper() + " to " + creds[env_key][var])
    os.environ[var.upper()] = creds[env_key][var]

# Call rclone with the required args
subprocess.check_call(["rclone"] + sys.argv[1:])
