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
from email.mime.text import MIMEText
import os
import sys
import smtplib
import socket
import subprocess
import tempfile
import time

# Find the path to the config and scripts directories via the path to this file
dir = os.path.dirname(sys.argv[0])
dir, _ = os.path.split(dir)
config_dir = os.path.join(dir, "config")
scripts_dir = os.path.join(dir, "scripts")

# Read the SMTP configuration
config = configparser.ConfigParser()
config.read(os.path.join(config_dir, "config.ini"))
if not 'smtp' in config:
    raise RuntimeError("Can't read smtp configuration")

# Create the logging file. Use a named file so it stays around if bad
# things happen, and so we can re-open it to read it.
log = tempfile.NamedTemporaryFile(prefix="daily", mode="w", delete=False)
logname = log.name

status = "OK"

scriptlist = ["backup.py"]
if time.strftime("%w") == "6":  # Saturday
    scriptlist.append("check.py")
scriptlist.append("remote_sync.py")

for script in scriptlist:
    exe = os.path.join(scripts_dir, script)
    script_status = subprocess.call([exe], stdout=log, stderr=subprocess.STDOUT)
    print("Script", script, "returned", script_status, file=log)
    if script_status != 0: status = "[FAIL]"

log.close()
log = open(logname, "r")
msg = MIMEText(log.read())
log.close()
os.unlink(log.name)

msg['Subject'] = status + " " + socket.gethostname() + \
                 time.strftime(": Nightly backup for %A %x")
msg['From'] = config['smtp']['mailfrom']
msg['To'] = config['smtp']['mailto']
if 'add_date' in config['smtp'] and config['smtp']['add_date']:
    msg['Date'] = email.utils.formatdate(localtime=True)

# Send the message via the SMTP server
s = smtplib.SMTP(config['smtp']['mailhost'])
s.sendmail(msg['From'], msg['To'], msg.as_string())
s.quit()
