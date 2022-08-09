#!/usr/bin/env python

# Bancal Samuel
# 2015-05-04

# Usage :
# /home/sbancal/py/2/bin/fab deploy pandoc


import os
from fabric.api import run, env, task  # cd
from fabric.contrib.project import rsync_project

# from fabric.operations import sudo

env.hosts = ["enacit1@enacit1-sysadmin"]

LOCAL_DIR = "/home/sbancal/Projects/ENACdrives/docs/"
REMOTE_DIR = "/data/web/enacit1-sysadmin/ENACdrives/"

MD_FILES = ("NEW_CLIENT_RELEASE.md",)
CSS = "/data/web/enacit1-sysadmin/markdown-pandoc.css"


@task
def ls():
    run("ls -l %s" % REMOTE_DIR)


@task
def deploy():
    rsync_project(
        local_dir=LOCAL_DIR,
        remote_dir=REMOTE_DIR,
        exclude=("*.git", "*.pyc"),
        # delete=True,
        extra_opts="--links",
    )


@task
def pandoc():
    for f in [os.path.join(REMOTE_DIR, f)[:-3] for f in MD_FILES]:
        run(
            "pandoc -s --self-contained --toc --toc-depth=2 -c %s -o %s.html %s.md"
            % (CSS, f, f)
        )
