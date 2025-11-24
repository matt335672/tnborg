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
from email.utils import formatdate
import os
import socket
import sys
import smtplib

# Find the path to the config via the path to this file
dir = os.path.dirname(sys.argv[0])
dir, _ = os.path.split(dir)
dir = os.path.join(dir, "config")

# Read the SMTP configuration
config = configparser.ConfigParser()
config.read(os.path.join(dir, "config.ini"))

msg = MIMEText("This is a test message")
msg['Subject'] = socket.gethostname() + ": Test message"
msg['From'] = config['smtp']['mailfrom']
msg['To'] = config['smtp']['mailto']
if 'add_date' in config['smtp'] and config['smtp']['add_date']:
    msg['Date'] = formatdate(localtime=True)

# Send the message via the SMTP server
s = smtplib.SMTP(config['smtp']['mailhost'])
s.sendmail(msg['From'], msg['To'], msg.as_string())
s.quit()
