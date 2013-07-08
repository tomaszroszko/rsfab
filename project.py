"""
    Helper functions to manage project on remote host
    All functions requires env.project_path to be setup.
    You can setup this var by using setup_project_path func
"""
import os
from contextlib import contextmanager as _contextmanager

from fabric.api import env, cd


def setup_project_path(project_path):
    env.project_path = project_path
    env.project_name = os.path.dirname(project_path)


@_contextmanager
def in_project():
    """
    Exec commands inside the project

    Example:
    with in_project():
        run("python manage.py syncdb --noinput" % env)
    """
    with cd(env.project_path):
        yield
