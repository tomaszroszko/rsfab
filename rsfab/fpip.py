"""
    Help Install project requirements.
    Requires requirements.txt file in env.project_path
    Requires env.project_path
    Requires env.virtualenv_path

    Install requirements only in vritualenv
"""
from fabric.operations import sudo, run
from project import in_project
from virtualenv import venv


def install_requirements(use_sudo=False, exists_action='i',
                         requirements='requirements.txt'):
    "Install the required packages from the requirements file using pip"
    func = use_sudo and sudo or run
    with venv():
        with in_project():
            func(
                "pip install -r %s --exists-action=%s" % (
                requirements, exists_action))


def install_lib(lib_name, use_sudo=False):
    """
        Install lib with given name
    """
    func = use_sudo and sudo or run
    with venv():
        with in_project():
            func("pip install %s" % lib_name)
