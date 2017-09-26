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

import unittest

import mock

from ebuild_util import Ebuild, Version
from ebuild_util.ebuild import remove_suffix
from numeric_version import NumericVersion


class TestRemoveSuffix(unittest.TestCase):
    def test_only_once(self):
        self.assertEqual(remove_suffix('azaz', 'az'), 'az')

    def test_order(self):
        self.assertEqual(remove_suffix('az', 'za'), 'az')


class TestVersion(unittest.TestCase):
    def test_str(self):
        self.assertEqual(str(Version(NumericVersion(1, 2), 3)), '1.2-r3')
        self.assertEqual(str(Version(NumericVersion(1, 2))), '1.2')

    def test_parse_parts(self):
        self.assertEqual(Version.parse_parts(('9999',)),
                         Version(NumericVersion(9999)))
        self.assertEqual(Version.parse_parts(('1.2.3',)),
                         Version(NumericVersion(1, 2, 3)))
        self.assertEqual(Version.parse_parts(('4.9', 'r2')),
                         Version(NumericVersion(4, 9), 2))
        with self.assertRaises(ValueError):
            Version.parse_parts('4.9-2')
        with self.assertRaises(ValueError):
            Version.parse_parts(('4.9', '2'))

    def test_parse_revision(self):
        self.assertEqual(Version.parse_revision('r123'), 123)
        with self.assertRaises(ValueError):
            Version.parse_revision('123')
        with self.assertRaises(ValueError):
            Version.parse_revision('r1a')

    def test_parse(self):
        self.assertEqual(Version.parse('4.9-r2'),
                         Version(NumericVersion(4, 9), 2))


class TestEbuild(unittest.TestCase):
    def test_from_full_path(self):
        path = '/foo/bar/mycat/mypkg/mypkg-1.2-r3.ebuild'
        ebuild = Ebuild.from_path(path)
        self.assertEqual(ebuild, Ebuild(
            package='mypkg',
            version=Version(NumericVersion(1, 2), 3),
            category='mycat',
            parent_path='/foo/bar'))

    def test_from_partial_path(self):
        path = 'mycat/mypkg/mypkg-1.2-r3.ebuild'
        ebuild = Ebuild.from_path(path)
        self.assertEqual(ebuild, Ebuild(
            package='mypkg',
            version=Version(NumericVersion(1, 2), 3),
            category='mycat'))

    def test_from_filename(self):
        path = 'mypkg-1.2-r3.ebuild'
        ebuild = Ebuild.from_path(path)
        self.assertEqual(ebuild, Ebuild(
            package='mypkg',
            version=Version(NumericVersion(1, 2), 3)))

    def test_many_dash(self):
        self.assertEqual(Ebuild.from_path('my-very-own-pkg-1.2-r3.ebuild'),
                         Ebuild(package='my-very-own-pkg',
                                version=Version(NumericVersion(1, 2), 3)))

    def test_many_dash_no_rev(self):
        self.assertEqual(Ebuild.from_path('my-very-own-pkg-1.2.ebuild'),
                         Ebuild(package='my-very-own-pkg',
                                version=Version(NumericVersion(1, 2))))

    def test_uprev(self):
        ebuild = Ebuild('mypkg', Version(NumericVersion(1, 2)))
        self.assertEqual(ebuild.version.revision, 0)
        ebuild.uprev()
        self.assertEqual(ebuild.version.revision, 1)
        ebuild.uprev()
        self.assertEqual(ebuild.version.revision, 2)

    def test_is_9999(self):
        ebuild = Ebuild('mypkg', Version(NumericVersion(9999)))
        self.assertTrue(ebuild.is_9999())

        ebuild = Ebuild('mypkg', Version(NumericVersion(9999), 1))
        self.assertFalse(ebuild.is_9999())

    @mock.patch('glob.glob', autospec=True)
    def test_find_in_dir(self, mock_glob):
        mock_glob.return_value = ('pkg-1.ebuild', 'pkg-9999.ebuild')

        self.assertEqual(list(Ebuild.find_in_directory('some/path')),
                         [Ebuild('pkg', Version(NumericVersion(1))),
                          Ebuild('pkg', Version(NumericVersion(9999)))])

        self.assertEqual(list(Ebuild.find_in_directory('some/path',
                                                       exclude_9999=True)),
                         [Ebuild('pkg', Version(NumericVersion(1)))])
