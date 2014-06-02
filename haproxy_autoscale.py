import logging
import urllib2
import boto.ec2
import boto.ec2.autoscale
from mako.template import Template


__version__ = '0.5'


def init_aws_ec2_conn(access_key, secret_key, region):
    """Initialize AWS ec2 connection"""

    return boto.ec2.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)


def init_aws_as_conn(access_key, secret_key, region):
    """Initialize AWS AS group connection"""

    return boto.ec2.autoscale.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)


def get_self_instance_id():
    """Get this instance's id."""

    logging.debug('get_self_instance_id()')
    response = urllib2.urlopen('http://169.254.169.254/1.0/meta-data/instance-id')
    instance_id = response.read()
    return instance_id


def list_as_instances(access_key, secret_key, region, autoscaling_group):
    """Return a list of instances of an autoscaling group"""

    aws_as = init_aws_as_conn(access_key, secret_key, region)
    aws_ec2 = init_aws_ec2_conn(access_key, secret_key, region)
    autoscaling_instances = []

    vm = aws_as.get_all_groups([autoscaling_group])
    autoscaling_instances_id = [j.instance_id for i in vm for j in i.instances]

    for instance_id in autoscaling_instances_id:
        vm = boto.ec2.instance.Instance(aws_ec2)
        vm.id = instance_id
        vm.update()
        autoscaling_instances.append(vm)

    return autoscaling_instances


def steal_elastic_ip(access_key, secret_key, region, ip):
    """Assign an elastic IP to this instance."""

    aws_ec2 = init_aws_ec2_conn(access_key, secret_key, region)

    logging.debug('steal_elastic_ip()')
    instance_id = get_self_instance_id()
    aws_ec2.associate_address(instance_id, ip)


def file_contents(filename=None, content=None):
    """
    Just return the contents of a file as a string or write if content
    is specified. Returns the contents of the filename either way.
    """
    logging.debug('file_contents()')
    if content:
        f = open(filename, 'w')
        f.write(content)
        f.close()
    
    try:
        f = open(filename, 'r')
        text = f.read()
        f.close()
    except:
        text = None

    return text


def generate_haproxy_config(template=None, instances=None):
    """Generate an haproxy configuration based on the template and instances list."""

    return Template(filename=template).render(instances=instances)