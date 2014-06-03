#!/usr/bin/python

from setuptools import setup

setup(name='haproxy-autoscale',
      version='0.5',
      description='HAProxy wrapper for handling auto-scaling EC2 instances.',
      author='Mark Caudill',
      author_email='mark@markcaudill.me',
      url='https://github.com/markcaudill/haproxy-update',
      install_requires=['boto>=2.0', 'mako>=0.5.0', 'argparse>=1.2.1'],
      license='MIT',
      py_modules=['haproxy_autoscale'],
      scripts=['update-haproxy.py'])
