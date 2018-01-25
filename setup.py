#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='brians-toontools',
    version=version,
    description='Open Authentication 2 support to Python-requests HTTP library.',
    long_description=open('README.md').read(),
    author='Brian Tilburgs',
    author_email='brian@tilburgs.net',
    url='https://github.com/briantilburgs/Brians-ToonTools',
    packages=find_packages(),
    install_requires=['requests', ],
    license='MIT',
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
    keywords=['toon', 'api', 'usage', 'verbruik', 'Oauth2'],
    zip_safe=False,
)
