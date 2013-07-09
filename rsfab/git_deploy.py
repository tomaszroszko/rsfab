"""
    Helper functions to setup project using git
    Requires project helper functions
    Requires env.git_branch or env.git_tag
    Requires env.git_url
"""
from fabric.api import sudo, run, env
from project import in_project


def git_checkout(use_sudo=False):
    """
        Checkout a branch or tag
    """
    func = use_sudo and sudo or run
    with in_project():
        if env.git_branch:
            func('git checkout %(git_branch)s' % env)
        else:
            func('git checkout %(git_tag)s' % env)


def git_reset(use_sudo=False):
    """
        Reset git to last version
    """
    func = use_sudo and sudo or run
    with in_project():
        func('git reset --hard')


def git_install_project(use_sudo=False):
    """
        Making a fresh clone from repo
    """
    func = use_sudo and sudo or run
    func('git clone %(git_url)s %(project_path)s' % env)
    git_checkout(use_sudo)


def git_update_project(use_sudo=False):
    """
        Update git repository
    """
    func = use_sudo and sudo or run
    with in_project():
        func('git pull')
    git_checkout(use_sudo)


def setup_git(git_url, git_branch=None, git_tag=None):
    """
        Setup requires vars for git
    """
    if git_branch is None and git_tag is None:
        raise ValueError('Git Branch or Git Tag need to be setuped')

    env.git_branch = git_branch
    env.git_tag = git_tag
    env.git_url = git_url