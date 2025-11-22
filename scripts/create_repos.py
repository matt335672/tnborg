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
import getpass
import logging
import os
import subprocess
import sys

# Logging object
log = None

# --------------------------------------------------------------------------
# M A K E   R E P O
# --------------------------------------------------------------------------
def make_repo(root,repo,src):
    repopath = os.path.join(root,repo)
    if os.path.isdir(repopath):
        log.info("Repo %s already exists",repopath)
    else:
        log.info("Creating %s",repopath)
        cmd = ["borg","init","-e","repokey",repopath]
        log.debug("Calling '%s'",str(cmd))
        subprocess.check_call(cmd)



# --------------------------------------------------------------------------
# M A I N
# --------------------------------------------------------------------------

# Set the logging up
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%T")
hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(formatter)
log = logging.getLogger("create_repos.py")
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
user=config["global"]["user"]
if user != getpass.getuser():
    raise RuntimeError("Script needs to be run as " + user)

for r in config["global"]["repos"].split():
    try:
        repos.append({
            "name" : r,
            "src"  : config[r]["src"],
            })
    except (configparser.NoSectionError,configparser.NoOptionError) as e:
        print(e,file=sys.stderr)

if not repos:
    raise RuntimeError("No actual repos were found to create!")

log.info("Found %d repos to create",len(repos))
status=0

if not os.path.isdir(repo_root):
    log.info("Creating repo root %s",repo_root)
    os.mkdir(repo_root)

for r in repos:
    try:
        make_repo(repo_root,r["name"],r["src"])

    except subprocess.CalledProcessError as e:
        if status == 0: status = e.returncode
    except OSError as e:
        log.error(str(e))
        if status == 0: status = e.errno

sys.exit(status)
