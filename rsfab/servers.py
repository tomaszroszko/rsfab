"""
    server side helpers
"""
from fabric.api import sudo


def apache_restart():
    sudo('/etc/init.d/apache2 restart')

def httpd_restart():
    sudo('/etc/init.d/httpd restart')