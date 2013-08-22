"""
    Helper functions to manage amazon cloud
"""
import boto.ec2
import boto.ec2.elb
import boto.rds

import time

from fabric.api import env, run
from fabric.exceptions import NetworkError
from fabric.context_managers import settings
from fabric.colors import red, green, blue
from fabric.utils import abort


def add_instance_to_balancer(balancer_name, instance):
    """
        add instnace to be available in balancer
    """
    print(green('Register instance %s from balancer %s' % (
        instance.id, balancer_name
    )))
    conn = get_elb_conn()
    balancer = conn.get_all_load_balancers(
        load_balancer_names=[balancer_name])[0]
    balancer.register_instances([instance.id])


def remove_instance_from_balancer(balancer_name, instance):
    """
        remove instance from balancer
    """
    print(green('Deregister instance %s from balancer %s' % (
        instance.id, balancer_name
    )))

    conn = get_elb_conn()
    balancer = conn.get_all_load_balancers(
        load_balancer_names=[balancer_name])[0]
    balancer.deregister_instances([instance.id])


def wait_for_vailable(obj, success_status=u'available'):
    """
        Wait for object availability and end when obj is avilable. Obj can
        be any amazon compotent like: image, instance, db instance or others
    """

    state = obj.update()
    while unicode(state) != success_status:
        print(blue('Wait for %s. Current status is:%s' % (
            unicode(obj), state)))
        time.sleep(env.aws_waiting_time)
        state = obj.update()


def wait_for_connection(ec2instance, attempts=3):
    """
        Try to connect with ec2
    """
    try:
        with settings(
                host_string=ec2instance.public_dns_name,
                user=env.user):
            run('pwd')
    except NetworkError:
        print(blue('Wait for connection %s:%s' %
                   (env.user, ec2instance.public_dns_name)))
        time.sleep(env.aws_waiting_time)
        if attempts:
            wait_for_connection(ec2instance, attempts - 1)
        else:
            print(red("Can't connect to ec2instance %s"
                      % ec2instance.public_dns_name))
            abort('Error')


def get_database():
    """
        get aws_db_instance_name from amazon
    """
    db_conn = boto.rds.connect_to_region(
        env.aws_region,
        aws_access_key_id=env.aws_access_key,
        aws_secret_access_key=env.aws_secret_access_key)
    db_instances = db_conn.get_all_dbinstances()
    db_instance = None
    for db in db_instances:
        if unicode(db.DBName) == env.aws_db_instance_name:
            db_instance = db
            break
    if db_instance is None:
        print(red('No DB instance found'))
    return db_instance


def get_ec2_conn():
    """
        Requried: env.aws_region, env.aws_access_key, env.aws_secret_access_key
        return conneciton to aws ec2
    """
    conn = boto.ec2.connect_to_region(
        env.aws_region,
        aws_access_key_id=env.aws_access_key,
        aws_secret_access_key=env.aws_secret_access_key
    )
    if conn is None:
        print(red("Can't connect to ec2 region"))
    return conn


def get_elb_conn():
    """
        Return conneciton to balancer
    """
    conn = boto.ec2.elb.ELBConnection(
        env.aws_access_key, env.aws_secret_access_key)
    if conn is None:
        print(red("Can't connect to balancer"))
    return conn


def get_instances():
    """
        Required: env.aws_env_tag and env.aws_env
        get list of instances for current environemnt
    """
    conn = get_ec2_conn()
    reservations = conn.get_all_instances(
        filters={'tag:%s' % env.aws_env_tag: env.aws_env})
    instances = []
    for r in reservations:
        instances.extend(r.instances)
    return instances


def run_instances():
    """
        It's run instance from ami_id. Wait for creating all instances
        and return their ids

        Requried parameters are:
        env.aws_run_templates - it's a list of templates to run on amazon

        aws_run_templates = [
            {
                'ami': 'ami-3df234d',
                'instance_type': 'm1.medium',
                'key_name': 'perfect-name-for-your-instance',
                'user_data': '''#!/bin/sh\necho export env=staging >> /etc/environment\n''',
                'security_groups': ['my-secure-group'],
                'placement': 'us-east1d',
                'callbacks': [func1, func2] #list of functions to run after creating the instance,
                 as parametr get boto Instance object,
                'tags': [{'key': 'value'}]
            }
        ]

    """
    conn = get_ec2_conn()
    instances = []

    for run_template in env.aws_run_templates:
        print(green('Starting Instance %s' % run_template['key_name']))
        image = conn.get_image(run_template['ami'])
        reservation = image.run(
            key_name=run_template['key_name'] % env,
            instance_type=run_template['instance_type'],
            user_data=run_template.get('user_data', None),
            security_groups=run_template['security_groups'],
            placement=run_template.get('placement', None)
        )
        instance = reservation.instances[0]
        instances.append((instance, run_template))
        tags = run_template.get('tags', [])
        for tag_key, tag_value in tags.items():
            instance.add_tag(tag_key, tag_value % env)

    for (instance, run_template) in instances:
        wait_for_vailable(instance, success_status=u'running')
        callbacks = run_template.get('callbacks', [])
        if callbacks:
            wait_for_connection(instance)
            for callback in callbacks:
                with settings(
                        host_string=instance.public_dns_name,
                        user=env.user):
                    callback(instance)
    return instances