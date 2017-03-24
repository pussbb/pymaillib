# -*- coding: utf-8 -*-
"""

"""
from distutils.command.build_ext import build_ext

from Cython.Build import cythonize
from setuptools import setup, find_packages
from setuptools.extension import Extension
import sys
import os

if sys.version_info < (3, 5):
    print("I'm only for 3, please upgrade")
    sys.exit(1)

ext = [
    Extension(
        'pymaillib.imap.pyimapparser',
        ["./pymaillib/imap/pyimapparser.pyx"],
        include_dirs=['./pymaillib/imap', '.'],
        language="c++",
        extra_compile_args=['-g', '-std=c++11']
    ),
    Extension(
        'pymaillib.imap.dovecot_utils',
        ['dovecot_utils.pyx'],
        include_dirs=['.', './dovecot_utils/'],
        define_macros=[('HAVE_UINTMAX_T', True), ('HAVE_UINT_FAST32_T', True)],
        extra_objects=['./dovecot_utils/build/libdovecot_utils.a'],
    )
]


setup(
    name='pymaillib',
    version='0.1',
    packages=find_packages(exclude=["tests"]),
    url='',
    license='WTFPL ',
    author='pussbb',
    author_email='pussbb@gmail.com',
    description='helper wrapper for imaplib',
    platforms=['linux-x86_64'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite="tests",
    install_requires=['python-dateutil'],
    ext_modules=cythonize(ext, force=True, language_level=3),
)
