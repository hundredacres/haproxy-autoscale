#!/usr/bin/python

import argparse
import configparser
import subprocess
import logging
import urllib2
from haproxy_autoscale import list_as_instances, file_contents, generate_haproxy_config, steal_elastic_ip


def main():
    # Parse up the command line arguments.
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a security group.')
    parser.add_argument('--config', default="/etc/haproxy-autoscale/haproxy-autoscale.conf",
                        help='Path to the config file.')
    parser.add_argument('--autoscaling-group', required=True, nargs='+', type=str)
    parser.add_argument('--region', default="us-east-1", help="AWS region name")
    parser.add_argument('--output', default='/etc/haproxy/haproxy.cfg',
                        help='Defaults to haproxy.cfg if not specified.')
    parser.add_argument('--template', default='/etc/haproxy-autoscale/haproxy.tpl')
    parser.add_argument('--haproxy', default='/usr/sbin/haproxy',
                        help='The haproxy binary to call. Defaults to haproxy if not specified.')
    parser.add_argument('--pid', default='/var/run/haproxy.pid',
                        help='The pid file for haproxy. Defaults to /var/run/haproxy.pid.')
    parser.add_argument('--eip',
                        help='The Elastic IP to bind to when VIP seems unhealthy.')
    parser.add_argument('--health-check-url',
                        help='The URL to check. Assigns EIP to self if health check fails.')
    args = parser.parse_args()

    # aws config file
    config_fh = open(args.config, "ro")
    config = configparser.RawConfigParser()
    config.read_file(config_fh)
    config_fh.close()

    access_key = config.get("credential", "access_key")
    secret_key = config.get("credential", "secret_key")

    # Fetch a list of all the instances in these security groups.
    instances = {}
    for autoscaling_group in args.autoscaling_group:
        logging.info('Getting instances for %s.' % autoscaling_group)
        instances[autoscaling_group] = list_as_instances(access_key, secret_key, args.region,
                                                         autoscaling_group)
    # Generate the new config from the template.
    logging.info('Generating configuration for haproxy.')
    new_configuration = generate_haproxy_config(args.template, instances)
    
    # See if this new config is different. If it is then restart using it.
    # Otherwise just delete the temporary file and do nothing.
    logging.info('Comparing to existing configuration.')
    old_configuration = file_contents(args.output)
    if new_configuration != old_configuration:
        logging.info('Existing configuration is outdated.')
        
        # Overwite the existing config file.
        logging.info('Writing new configuration.')
        file_contents(args.output, generate_haproxy_config(args.template, instances))
        
        # Get PID if haproxy is already running.
        logging.info('Fetching PID from %s.' % args.pid)
        pid = file_contents(args.pid)
        
        # Restart haproxy.
        logging.info('Restarting haproxy.')
        command = '''%s -p %s -f %s -sf %s''' % (args.haproxy, args.pid, args.output, pid or '')
        logging.info('Executing: %s' % command)
        subprocess.call(command, shell=True)
    else:
        logging.info('Configuration unchanged. Skipping restart.')
    
    # Do a health check on the url if specified.
    try:
        if args.health_check_url and args.eip:
            logging.info('Performing health check.')
            try:
                logging.info('Checking %s' % args.health_check_url)
                response = urllib2.urlopen(args.health_check_url)
                logging.info('Response: %s' % response.read())
            except:
                # Assign the EIP to self.
                logging.warn('Health check failed. Assigning %s to self.' % args.eip)
                steal_elastic_ip(access_key, secret_key, args.eip)
    except:
        pass


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
