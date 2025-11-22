#!/bin/sh
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

# Script to use as ~tnborg/bin/borg to chain to the required
# borg executable.
#
# We can't use a soft-link for this on TrueNAS 25.04, as a bug in
# sudo results in this message when running borg in a sudo session:-
#
# sudo: argv[0] mismatch, expected "/path/to/borg.exe", got "borg"
#
# The bug https://bugzilla.sudo.ws/show_bug.cgi?id=1050 is fixed in sudo 1.9.14

# Edit this line as appropriate
BORG_EXE=/path/to/borg.exe

# Uncomment this if necessary
#USING_ONE_FILE_BORG=1

if [ "$USING_ONE_FILE_BORG" ]; then
    # Set $TEMP to something writeable without the 'noexec' mount attribute
    TEMP_ROOT=/run/user/$(id -u)
    if ! [ -d "$TEMP_ROOT" ]; then
        # User may have been started with su/sudo
        echo "** Warning: Borg being unpacked onto disk" >&2
        TEMP_ROOT="$HOME"
    fi
    export TEMP="$TEMP_ROOT/borgtmp"
    if ! [ -d "$TEMP" ]; then
        mkdir "$TEMP" || exit $?
    fi
fi

exec $BORG_EXE "$@"
