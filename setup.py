# -*- coding: utf-8 -*-
"""

"""

from setuptools import setup
import sys


if sys.version_info < (3, 5):
    print("I'm only for 3, please upgrade")
    sys.exit(1)


setup(
    name='pymaillib',
    version='0.1',
    packages=['pymaillib', ],
    url='',
    license='WTFPL ',
    author='pussbb',
    author_email='pussbb@gmail.com',
    description='helper wrapper for imaplib',
    platforms='any',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite="tests",
    install_requires=['python-dateutil'],

)
