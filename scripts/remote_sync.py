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
import logging
import os
import getpass
import subprocess
import sys
import time

# Logging object
log = None

# --------------------------------------------------------------------------
# S Y N C   R E P O
# --------------------------------------------------------------------------
def sync_repo(root, remote, repo):
    repopath=os.path.join(root,repo)
    bucket_name = repo + "-backup-vocalistic-com"
    cmd = ["rclone","sync",repopath,remote + ":" + bucket_name, "--fast-list"]
    log.debug("Calling '%s'",str(cmd))
    subprocess.check_call(cmd)



# --------------------------------------------------------------------------
# M A I N
# --------------------------------------------------------------------------

# Set the logging up
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%T")
hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(formatter)
log = logging.getLogger("remote_sync.py")
log.addHandler(hdlr)
#log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)

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

# Read the repos
repos = []
config.read(os.path.join(dir,"config.ini"))
repo_root=config["global"]["root"]
repos=config["global"]["repos"].split()
user=config["global"]["user"]
if user != getpass.getuser():
    raise RuntimeError("Script needs to be run as " + user)

log.info("Found %d repos to sync",len(repos))
status = 0
for r in repos:
    try:
        sync_repo(repo_root, remote, r)

    except subprocess.CalledProcessError as e:
        if status == 0: status = e.returncode
    except OSError as e:
        log.error(str(e))
        if status == 0: status = e.errno

log.info("Finish sync, status=%d",status)
sys.exit(status)
