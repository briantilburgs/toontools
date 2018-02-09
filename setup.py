#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.2.0'

setup(
    name='toontools',
    version=version,
    description='Python modules for connecting to Toon van Eneco',
    long_description=open('README.md').read(),
    author='Brian Tilburgs',
    author_email='brian@tilburgs.net',
    url='https://github.com/briantilburgs/toontools',
    packages=find_packages(),
    install_requires=['requests', 'pynteractive', 'certifi', 'webbrowser', 'xlsxwriter'],
    license='MIT',
    classifiers=(
        "Development Status :: 3 - Alpha",
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
