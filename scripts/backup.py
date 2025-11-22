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

# See https://stackoverflow.com/questions/431684/how-do-i-cd-in-python/13197763
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# Logging object
log = None

# --------------------------------------------------------------------------
# M A K E   B A C K U P
# --------------------------------------------------------------------------
def make_backup(archive,root,repo,src):
    with cd(src):
        log.info("Creating %s::%s",repo,archive)
        repopath = os.path.join(root,repo)
        cmd = ["borg","create","-x","--show-rc",repopath + "::" + archive,"."]
        log.debug("Calling '%s'",str(cmd))
        subprocess.check_call(cmd)


# --------------------------------------------------------------------------
# P R U N E   R E P O
# --------------------------------------------------------------------------
def prune_repo(root,repo,prune_args):
    cmd = ["borg","prune","--show-rc",]
    cmd.extend(prune_args.split())
    cmd.append(os.path.join(root,repo))
    log.debug("Calling '%s'",str(cmd))
    subprocess.check_call(cmd)


# --------------------------------------------------------------------------
# M A I N
# --------------------------------------------------------------------------

# Set the logging up
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%T")
hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(formatter)
log = logging.getLogger("backup.py")
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
os.environ["PATH"] += os.pathsep + config["global"]["extra_path"]

# Read the creds-file and configure the environment
creds = configparser.ConfigParser()
creds.read(os.path.join(dir, "creds.ini"))
os.environ["BORG_PASSPHRASE"] = creds["borg-creds"]["passphrase"]

# Read the repos
repos = []
repo_root=config["global"]["root"]
prune_args=config["global"]["prune_args"]
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
    raise RuntimeError("No actual repos were found to back up!")

log.info("Found %d repos to back up",len(repos))
archive_name = time.strftime("%Y-%m-%d")
status=0
for r in repos:
    try:
        make_backup(archive_name,repo_root,r["name"],r["src"])
        prune_repo(repo_root,r["name"],prune_args)

    except subprocess.CalledProcessError as e:
        if status == 0: status = e.returncode
    except OSError as e:
        log.error(str(e))
        if status == 0: status = e.errno

log.info("Finish backup, status=%d",status)
sys.exit(status)
