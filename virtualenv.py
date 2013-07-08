"""
    Helper functions for managing virtualenvs
    All functions requires env.virtualenv_path to be setup.
    You can setup this var by using setup_venv(path_to_venv)
"""
from contextlib import contextmanager as _contextmanager

from fabric.api import env, prefix, task, run
from fabric.contrib.files import exists
from fabric.operations import sudo


@task
def create_venv(use_sudo=False):
    """
    Create new virtualenv only if virtualenv_path is not exists

    --no-site-packages it's depreceted b'coz in new virtualenv it's default
    behaviour so we don't use this parametr over here
    """

    func = use_sudo and sudo or run

    if not exists(env.virtualenv_path):
        func('virtualenv %(virtualenv_path)s' % env)


def setup_venv(virtualenv_path):
    """
        setup virtualenv_path in env
    """
    env.virtualenv_path = virtualenv_path


@_contextmanager
def venv():
    """
    Exec commands inside virtual env

    Example:
    with venv():
        run("python manage.py syncdb --noinput" % env)
    """
    venv_activate = "source %(virtualenv_path)s/bin/activate" % env
    with prefix(venv_activate):
        yield