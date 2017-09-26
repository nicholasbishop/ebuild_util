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

"""Simple ebuild file utilities."""

# pylint: disable=too-few-public-methods

import copy
import glob
import os

import attr
from attr import validators

from numeric_version import NumericVersion

def remove_suffix(string, suffix):
    """Strip the given suffix from a string.

    Unlike the builtin string rstrip method the suffix is treated as a
    string, not a character set. Only an exact match triggers a
    removal, and the suffix is only removed once.

    Examples:

        remove_suffix('azaz', 'az') -> 'az'
        remove_suffix('az', 'za') -> 'az'
    """
    if string.endswith(suffix):
        return string[:-len(suffix)]
    return string


@attr.s(slots=True)
class Version(object):
    """Ebuild primary version and optional revision."""
    primary = attr.ib(validator=validators.instance_of(NumericVersion))
    revision = attr.ib(default=0, validator=validators.instance_of(int))

    def __str__(self):
        suffix = ''
        if self.revision > 0:
            suffix = '-r' + str(self.revision)
        return str(self.primary) + suffix

    @classmethod
    def parse(cls, string):
        """Parse an ebuild |Version| from a string."""
        return cls.parse_parts(string.split('-'))

    @staticmethod
    def parse_revision(string):
        """Parse a revision |string| such as "r300"."""
        if not string.startswith('r'):
            raise ValueError('invalid revision: ' + string)
        string = string[1:]
        return int(string)

    @classmethod
    def parse_parts(cls, parts):
        """Parse an ebuild |Version| from a list of strings.

        Examples:

            ('9999',) -> Version(NumericVersion(9999))
            ('1.2.3',) -> Version(NumericVersion(1.2.3))
            ('4.9', 'r2') -> Version(NumericVersion(4.9, 2))
        """
        if len(parts) not in (1, 2):
            raise ValueError('invalid ebuild version format: ' + parts)

        primary = NumericVersion.parse(parts[0])

        # Get the revision if present
        rev = 0
        if len(parts) == 2:
            rev = cls.parse_revision(parts[1])

        return cls(primary, rev)


@attr.s(slots=True)
class Ebuild(object):
    """Ebuild info / paths / simple content manipulation."""
    EXTENSION = '.ebuild'

    package = attr.ib()
    version = attr.ib(validator=validators.instance_of(Version))
    category = attr.ib(default=None)
    parent_path = attr.ib(default=None)

    @classmethod
    def from_path(cls, path):
        """Create an Ebuild object by parsing |path|."""
        pkgdir, filename = os.path.split(path)
        catdir, pkgname = os.path.split(pkgdir)
        parent_path, catname = os.path.split(catdir)
        if parent_path == '':
            parent_path = None
        if catname == '':
            catname = None

        ebuild = cls.from_filename(filename)

        if pkgname != '' and pkgname != ebuild.package:
            raise ValueError('invalid ebuild path: ' + path)

        ebuild.parent_path = parent_path
        ebuild.category = catname

        return ebuild


    @classmethod
    def from_filename(cls, filename):
        """Create an Ebuild object by parsing an ebuild |filename|."""

        # Strip the suffix
        no_suffix = remove_suffix(filename, cls.EXTENSION)

        maxsplits = 2
        parts = no_suffix.rsplit('-', maxsplits)
        pkgname = parts[0]
        version = None

        # Try to parse a version with a revision number
        if len(parts) == 3:
            try:
                version = Version.parse_parts(parts[1:])
            except ValueError:
                pkgname = '-'.join(parts[:2])

        # Version doesn't have a revision number, parse it from just
        # the last part
        if version is None:
            version = Version.parse_parts(parts[-1:])

        return cls(pkgname, version)

    @property
    def path(self):
        """Get full ebuild path."""
        rest = os.path.join(self.category, self.package, self.filename)
        if self.parent_path:
            return os.path.join(self.parent_path, rest)
        return rest

    @property
    def filename(self):
        """Get just the ebuild filename."""
        return '{}-{}.{}'.format(self.package, str(self.version),
                                 self.EXTENSION)

    def copy(self):
        """Return a copy of the Ebuild object."""
        return copy.deepcopy(self)

    def read(self):
        """Get the contents of the file."""
        with open(self.path) as rfile:
            return rfile.read()

    def write(self, stuff):
        """Set the contents of the file."""
        with open(self.path, 'w') as wfile:
            return wfile.write(stuff)

    def stabilized_content(self):
        """Copy and modify unstable contents to be stable."""
        if not self.is_9999():
            raise KeyError('source for stabilizing must be unstable')
        keywords_stable = 'KEYWORDS="*"'
        keywords_unstable = 'KEYWORDS="~*"'
        content = self.read()
        # Sanity check
        count = content.count(keywords_unstable)
        if count != 1:
            raise RuntimeError('unexpected keyword count in ebuild', count)
        return content.replace(keywords_unstable, keywords_stable)

    @property
    def revision(self):
        """Get the ebuild's revision, or zero if is doesn't have one."""
        return self.version.revision

    def is_9999(self):
        """Whether the ebuild is a 9999 ebuild."""
        version = NumericVersion(9999)
        return self.version.primary == version and self.revision == 0

    def is_symlink(self):
        """Whether the ebuild is a symlink."""
        return os.path.islink(self.path)

    def uprev(self):
        """Bump the revision of the ebuild."""
        # As of pylint 1.7.2 the revision field is incorrectly flagged
        # as not being a valid slot
        #
        # pylint: disable=assigning-non-slot
        self.version.revision += 1

    @staticmethod
    def find_in_directory(root, exclude_9999=False):
        """Get all the Ebuilds in the given directory.

        If |exclude_9999| is True then any ebuild with an exact
        version of 9999 will be excluded from the results. By default
        9999 ebuilds are included in the results.
        """
        paths = glob.glob(os.path.join(root, '*{}'.format(Ebuild.EXTENSION)))
        for path in paths:
            ebuild = Ebuild.from_path(path)
            if exclude_9999 and ebuild.is_9999():
                continue
            yield ebuild

    def __str__(self):
        return self.path
