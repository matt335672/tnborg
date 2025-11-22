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
# C H E C K   R E P O
# --------------------------------------------------------------------------
def check_repo(root,repo):
    log.info("Checking %s",repo)
    repopath = os.path.join(root,repo)
    cmd = ["borg","check",repopath]
    log.debug("Calling '%s'",str(cmd))
    # Disable stderr logging for now, or the log fills with progress messages!
    # This is fixed in the next borg release.
    subprocess.check_call(cmd,stderr=open("/dev/null","w"))


# --------------------------------------------------------------------------
# M A I N
# --------------------------------------------------------------------------

# Set the logging up
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%T")
hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(formatter)
log = logging.getLogger("check.py")
log.addHandler(hdlr)
#log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)

# Find the path to the config via the path to this file
dir = os.path.dirname(sys.argv[0])
dir, _ = os.path.split(dir)
dir = os.path.join(dir, "config")

# Read the config and update the PATH
config = configparser.ConfigParser()
config.read(os.path.join(dir,"config.ini"))
os.environ["PATH"] += os.pathsep + config["global"]["extra_path"]

# Read the creds-file and configure the environment
creds = configparser.ConfigParser()
creds.read(os.path.join(dir, "creds.ini"))
os.environ["BORG_PASSPHRASE"] = creds["borg-creds"]["passphrase"]

# Read the repos
repos = []
repo_root=config["global"]["root"]
repos=config["global"]["repos"].split()
user=config["global"]["user"]
if user != getpass.getuser():
    raise RuntimeError("Script needs to be run as " + user)

if not repos:
    raise RuntimeError("No actual repos were found to check!")

log.info("Found %d repos to check",len(repos))
status=0
for r in repos:
    try:
        check_repo(repo_root,r)

    except subprocess.CalledProcessError as e:
        if status == 0: status = e.returncode
        log.error("Check of %s returned %d",r,e.returncode)

log.info("Finish check, status=%d",status)
sys.exit(status)
