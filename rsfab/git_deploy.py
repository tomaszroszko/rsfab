"""
    Helper functions to setup project using git
    Requires project helper functions
    Requires env.git_branch or env.git_tag
    Requires env.git_url
"""
import os, re

from fabric.api import sudo, run, env
from fabric.operations import get
from project import in_project


GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
GIT_LOG_FORMAT = '%x1f'.join(['%H', '%an', '%ae', '%ad', '%s']) + '%x1e'
GIT_LOG_FILENAME = 'git_log.txt'

#to get ticets from commimt messages
TICET_PATERN = re.compile('#(\d+)')


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
        if env.git_branch:
            func('git pull')
        else:
            func('git fetch --tags')
        git_checkout(use_sudo)


def get_current_id(use_sudo=False):
    """

    :return:
    """
    func = use_sudo and sudo or run
    with in_project():
        id = func('git rev-parse HEAD')
    return id


def get_logs(since=None, use_sudo=False):
    """
        save formated git logs to file in project_path, read all logs,
        delete tmp file, create a dict and return all logs
    """
    func = use_sudo and sudo or run
    command = 'git log --format="%s"' % GIT_LOG_FORMAT
    if since:
        command += ' %(since)s..HEAD' % {'since': since}
    command += ' > ' + GIT_LOG_FILENAME
    with in_project():
        func(command)
        get(os.path.join(env.project_path, GIT_LOG_FILENAME), GIT_LOG_FILENAME)
        f = open(GIT_LOG_FILENAME, 'r')
        r = f.readlines()
        f.close()
        os.remove(GIT_LOG_FILENAME)

    log = [row.strip().split("\x1f") for row in r]
    log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]
    return log


def get_ticets(since=None, use_sudo=False):
    """
        return ticets numbers from git messages
    """
    tickets = {}
    for log in get_logs(since, use_sudo):
        if log.get('message'):
            commit_tickets = TICET_PATERN.findall(log['message'])
            for ticket in commit_tickets:
                if not ticket in tickets.keys():
                    tickets[ticket] = {'revisions': [], 'servers': []}
                tickets[ticket]['revisions'].append(log['id'])
    return tickets


def setup_git(git_url, git_branch=None, git_tag=None):
    """
        Setup requires vars for git
    """
    if git_branch is None and git_tag is None:
        raise ValueError('Git Branch or Git Tag need to be setuped')

    env.git_branch = git_branch
    env.git_tag = git_tag
    env.git_url = git_url
