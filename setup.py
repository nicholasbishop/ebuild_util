# Copyright 2017 Neverware Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=missing-docstring

from os import path
from setuptools import setup


SCRIPT_PATH = path.abspath(path.dirname(__file__))


def read_readme():
    """Get the contents of the README.rst file."""
    readme_path = path.join(SCRIPT_PATH, 'README.rst')
    with open(readme_path) as rfile:
        return rfile.read()


setup(
    name='ebuild_util',
    version='1.0.0',
    description='Utilities for ebuild files',
    long_description=read_readme(),
    url='https://github.com/nicholasbishop/ebuild_util',
    author='Nicholas Bishop',
    author_email='nicholasbishop@gmail.com',
    license='Apache 2.0',
    packages=['ebuild_util'],
    install_requires=['attrs>=17.0.0', 'numeric-version>=1.0.3'],
)
