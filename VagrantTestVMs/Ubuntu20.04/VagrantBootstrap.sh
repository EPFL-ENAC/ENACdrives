#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get dist-upgrade -y
apt-get install -y ubuntu-desktop firefox
apt-get install -y gcc make perl

# Do it by hand :
# Finaly set the right keyboard in the settings
