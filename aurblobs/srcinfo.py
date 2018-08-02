import io

from collections import defaultdict


class Package(object):
    __slots__ = (
        'name',
        'desc',
        'arch',
        'url',
        'license',
        'groups',
        'depends',
        'opt_depends',
        'provides',
        'conflicts',
        'replaces',
        'backup',
        'options',
        'install',
        'changelog',
    )

    def __init__(self, name):
        self.name = name

        self.desc = None
        self.arch = []
        self.url = None
        self.license = []
        self.groups = []
        self.depends = defaultdict(list)
        self.opt_depends = defaultdict(list)
        self.provides = defaultdict(list)
        self.conflicts = defaultdict(list)
        self.replaces = defaultdict(list)
        self.backup = []
        self.options = []
        self.install = None
        self.changelog = None


class PackageBase(Package):
    __slots__ = (
        'ver',
        'rel',
        'epoch',
        'source',
        'valid_pgp_keys',
        'no_extract',
        'md5sums',
        'sha1sums',
        'sha224sums',
        'sha256sums',
        'sha384sums',
        'sha512sums',
        'make_depends',
        'check_depends',
    )

    def __init__(self, name):
        super().__init__(name)

        self.ver = None
        self.rel = None
        self.epoch = None
        self.source = defaultdict(list)
        self.valid_pgp_keys = []
        self.no_extract = []
        self.md5sums = defaultdict(list)
        self.sha1sums = defaultdict(list)
        self.sha224sums = defaultdict(list)
        self.sha256sums = defaultdict(list)
        self.sha384sums = defaultdict(list)
        self.sha512sums = defaultdict(list)
        self.make_depends = defaultdict(list)
        self.check_depends = defaultdict(list)


class Srcinfo(object):
    __slots__ = (
        'base',
        'packages',
    )

    def __init__(self):
        self.base = None
        self.packages = []


def parse(file: io.TextIOBase):
    srcinfo = Srcinfo()

    current = None

    for line in file:
        line = line.strip()

        if line == '' or line.startswith('#'):
            continue

        try:
            (key, value) = line.split('=', 1)
        except ValueError:
            raise SyntaxError('Invalid line: ' + line)

        (key, value) = (key.strip(), value.strip())

        print('key = "%s", value = "%s"' % (key, value))

        if key == 'pkgbase':
            if srcinfo.base is not None:
                raise SyntaxError('Duplicated pkgbase: %s' % line)

            current = PackageBase(name=value)
            srcinfo.base = current

            continue

        elif key == 'pkgname':
            if srcinfo.base is None:
                raise SyntaxError('Missing pkgbase: %s' % line)

            current = Package(name=value)
            srcinfo.packages.append(current)

            continue

        else:
            if '_' in key:
                (key, arch) = key.split('_', 1)

                if arch == 'any' or arch not in srcinfo.base.arch:
                    raise SyntaxError('Invalid arch "%s" on key "%s"' % (arch, key))

            else:
                (key, arch) = (key, None)

            if isinstance(current, PackageBase):
                if (key, arch) == ('pkgver', None):
                    current.ver = value
                    continue
                elif (key, arch) == ('pkgrel', None):
                    current.rel = value
                    continue
                elif (key, arch) == ('epoch', None):
                    current.epoch = value
                    continue
                elif key == 'source':
                    current.source[arch].append(value)
                    continue
                elif (key, arch) == ('validpgpkeys', None):
                    current.valid_pgp_keys.append(value)
                    continue
                elif (key, arch) == ('noextract', None):
                    current.no_extract.append(value)
                    continue
                elif key == 'md5sums':
                    current.md5sums[arch].append(value)
                    continue
                elif key == 'sha1sums':
                    current.sha1sums[arch].append(value)
                    continue
                elif key == 'sha224sums':
                    current.sha224sums[arch].append(value)
                    continue
                elif key == 'sha256sums':
                    current.sha256sums[arch].append(value)
                    continue
                elif key == 'sha384sums':
                    current.sha384sums[arch].append(value)
                    continue
                elif key == 'sha512sums':
                    current.sha512sums[arch].append(value)
                    continue
                elif key == 'makedepends':
                    current.makedepends[arch].append(value)
                    continue
                elif key == 'checkdepends':
                    current.checkdepends[arch].append(value)
                    continue

            if isinstance(current, Package):
                if (key, arch) == ('pkgdesc', None):
                    current.desc = value
                    continue
                elif (key, arch) == ('arch', None):
                    current.arch.append(value)
                    continue
                elif (key, arch) == ('url', None):
                    current.url = value
                    continue
                elif (key, arch) == ('license', None):
                    current.license.append(value)
                    continue
                elif (key, arch) == ('groups', None):
                    current.groups.append(value)
                    continue
                elif key == 'depends':
                    current.depends[arch].append(value)
                    continue
                elif key == 'optdepends':
                    current.opt_depends[arch].append(value)
                    continue
                elif key == 'provides':
                    current.provides[arch].append(value)
                    continue
                elif key == 'conflicts':
                    current.conflicts[arch].append(value)
                    continue
                elif key == 'replaces':
                    current.replaces[arch].append(value)
                    continue
                elif key == 'backup':
                    current.backup[arch].append(value)
                    continue
                elif key == 'options':
                    current.options[arch].append(value)
                    continue
                elif key == 'install':
                    current.install[arch].append(value)
                    continue
                elif key == 'changelog':
                    current.changelog[arch].append(value)
                    continue

            raise SyntaxError('Unknown property: %s' % line)

    return srcinfo
