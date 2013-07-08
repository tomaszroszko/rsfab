"""
    Rsync helper functions
"""
from fabric.api import env
from fabric.contrib.project import rsync_project


def rsync_update_project():
    rsync_project(
        remote_dir=env.project_path,
        exclude=env.rsync_exclude
    )


def setup_rsync(rsync_exclude):
    """
        setup all needed vars
    """

    env.rsync_exclude = rsync_exclude