"""
    Rsync helper functions
"""
import os

from fabric.api import env
from fabric.contrib.project import rsync_project


def rsync_update_project():
    rsync_project(
        remote_dir=env.project_path,
        local_dir=env.rsync_local,
        exclude=env.rsync_exclude
    )


def setup_rsync(rsync_exclude, rsync_local):
    """
        setup all needed vars
    """

    env.rsync_exclude = rsync_exclude
    env.rsync_local = rsync_local