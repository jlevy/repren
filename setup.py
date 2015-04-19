#!/usr/bin/env

from setuptools import setup, find_packages
import imp

repren = imp.load_source("repren", "repren")

setup(
  name="repren",
  version=repren.VERSION,
  packages=find_packages(),
  author="Joshua Levy",
  license="Apache 2",
  url="https://github.com/jlevy/repren",
  download_url="https://github.com/jlevy/repren/tarball/" + repren.VERSION,
  scripts=["repren"],
  install_requires=[],
  description=repren.DESCRIPTION,
  long_description=repren.LONG_DESCRIPTION,
  classifiers= [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python :: 2.7',
    'Topic :: Utilities',
    'Topic :: Text Processing',
    'Topic :: Software Development'
  ],
)
