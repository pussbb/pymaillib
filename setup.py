# -*- coding: utf-8 -*-
"""

"""
from distutils.command.build_ext import build_ext

from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension
import sys


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
    )
]


class InlineBuildExtCommand(build_ext):
    """Runs build_ext command with --inline command argument

    """

    def run(self):
        """Run build_ext command

        :return:
        """
        self.inplace = 1
        build_ext.run(self)

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
    ext_modules=cythonize(ext, force=True, language_level=3),
    cmdclass={
        'build_ext': InlineBuildExtCommand,
    },
)
