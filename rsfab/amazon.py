"""
    Helper functions to manage amazon cloud
"""
import boto.ec2
import time

from fabric.api import env
from fabric.context_managers import settings
from fabric.colors import red, green, blue


def wait_for_vailable(obj):
    """
        Wait for object availability and end when obj is avilable. Obj can
        be any amazon compotent like: image, instance, db instance or others
    """

    state = obj.update()
    while unicode(state) != u'available':
        print(blue('Wait for %s. Current status is:%s' % (
            unicode(obj), state)))
        time.sleep(env.aws_waiting_time)
        state = obj.update()


def run_instances():
    """
        It's run instance from ami_id. Wait for creating all instances
        and return their ids

        Requried parameters are:
        env.aws_ami_id - ami id from we need to run new instance
        env.aws_run_templates - it's a list of templates to run on amazon

        aws_run_templates = [
            {
                'instance_type': 'm1.medium',
                'key_name': 'perfect-name-for-your-instance',
                'user_data': '''#!/bin/sh\necho export env=staging >> /etc/environment\n''',
                'security_groups': ['my-secure-group'],
                'callbacks': [func1, func2] #list of functions to run after creating the instance,
                 as parametr get boto Instance object,
                'tags': {'key': 'value'}
            }
        ]

    """
    conn = boto.ec2.connect_to_region(
        env.aws_region,
        aws_access_key_id=env.aws_access_key,
        aws_secret_access_key=env.aws_secret_access_key
    )
    if conn is None:
        print(red("Can't connect to ec2 region"))
        return

    image = conn.get_image(env.aws_ami)
    instances = []

    for run_template in env.run_templates:
        print(green('Starting Instance %s' % run_template['key_name']))
        reservation = image.run(
            key_name=run_template['key_name'],
            instance_type=run_template['instance_type'],
            user_data=run_template.get('user_data', None),
            security_groups=run_template['security_groups']
        )
        instances.append((reservation.instances[0], run_template))

    for (instance, run_template) in instances:
        wait_for_vailable(instance)
        callbacks = run_template.get('callbacks', [])
        if callbacks:
            for callback in callbacks:
                with settings(host_string=instance.endpoint):
                    callback(instance)
    return instances