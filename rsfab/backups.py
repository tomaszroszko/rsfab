"""
Helpers functions for doing backups
Requires env.backup_dir
"""
import os
from datetime import datetime
from fabric.api import env, sudo, run
from fabric.decorators import task


@task
def initial_backup(use_sudo=False):
    """
        Changes project_path directory
        and install the project in backup_dir.
    """
    current_datetime = datetime.now()

    env.original_project_path = env.project_path
    env.project_path = os.path.join(
        env.backup_dir,
        env.project_name,
        current_datetime.strftime('%Y%m%d%H%M'))
    env.backup_path = env.project_path


@task
def finish_backup(use_sudo=False):
    """
        make a symlink from original project path to backup
    """
    func = use_sudo and sudo or run

    func('rm %(original_project_path)s' % env)
    func('ln -s %(original_project_path)s %(backup_path)s' % env)


@task
def revert_backup(use_sudo=False):
    """
        revert a backup get last copy and try todo backup
    """
    func = use_sudo and sudo or run

    env.backup_path = os.path.join(
        env.backup_dir, func('ls -1 %(backup_dir)s' % env).split()[1])
    finish_backup(use_sudo)

@task
def safe_copy(use_sudo=False):
    """
    Create safe copy of current project path to backup dir
    """
    func = use_sudo and sudo or run
    env.project_backup = env.backup_dir + datetime.now().strftime(
        '%Y%m%d_%H%M')
    func('cp -R %(project_path)s %(project_backup)s' % env)

def setup_backup(backup_dir):
    """
        Setup vars needed for backup.
    """
    env.backup_dir = backup_dir
