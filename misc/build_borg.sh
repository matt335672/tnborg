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

set -e

# General parameters
BORG_VERSION=1.4.2    ; # Borg version to build
BOX=bookworm          ; # Debian version to use
PROVIDER=libvirt      ; # Vagrant box provider

# Vagrantfile parameters. Adjust to suit
export VMCPUS=8      ; # Number of CPUs
export XDISTN=$VMCPUS; # Workers for pytest

# Other globals
TARGET_TARDIR=borg-dir-$BORG_VERSION
TARGET_FILE="$(pwd)"/$TARGET_TARDIR.tgz
BUILD_DIR=/tmp/build_borg.$$

# Can we write to the current directory?
if ! [ -w . ]; then
    echo "** Current directory is not writeable" >&2
    exit 1
fi

echo "-- Creating build directory"
rm -rf "$BUILD_DIR"
mkdir "$BUILD_DIR"
cd "$BUILD_DIR"

echo "-- Fetching release $BORG_VERSION"
wget https://github.com/borgbackup/borg/releases/download/$BORG_VERSION/borgbackup-$BORG_VERSION.tar.gz -O borgtmp.tar
tar xf borgtmp.tar
rm -r borgtmp.tar
# Rename directory to make it easier to remove later
mv borgbackup-$BORG_VERSION build

echo "-- Fetching Vagrantfile"
cd build
wget https://raw.githubusercontent.com/borgbackup/borg/refs/tags/$BORG_VERSION/Vagrantfile -O Vagrantfile

if [ "$PROVIDER" != virtualbox ]; then
    echo "-- Patching Vagrantfile"
    sed -ie 's/:virtualbox/:'$PROVIDER'/' Vagrantfile
fi

echo "-- Setting up vagrant"
plugin_list="vagrant-scp"
case "$PROVIDER" in
    hyperv | docker | virtualbox)
        # Native provider available
        ;;
    *)  plugin_list="$plugin_list vagrant-$PROVIDER"
        ;;
esac
# shellcheck disable=SC2086
vagrant plugin install $plugin_list
vagrant up $BOX

echo "-- Getting release"
vagrant scp $BOX:/vagrant/borg/borg.tgz ../borg-$BORG_VERSION.tgz

echo "-- Cleaning up"
vagrant destroy -f $BOX
cd ..
rm -rf build

echo "- Repacking tarfile"
tar xf ./borg-$BORG_VERSION.tgz
mv borg-dir $TARGET_TARDIR
tar czf "$TARGET_FILE" $TARGET_TARDIR
cd
rm -rf $BUILD_DIR

echo "All done! release is in ./$TARGET_FILE"
