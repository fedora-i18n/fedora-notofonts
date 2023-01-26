# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Genspec sub-command module."""

import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
try:
    from notorepos import NotoRepos
except ImportError:
    from pyfednotofonts.notorepos import NotoRepos
import pyfontrpmspec.errors as err
import pyfontrpmspec.generator as gen
from pyfontrpmspec.messages import Message as m
from pyfontrpmspec.package import Package


class FnSubCmdGenSpec(FnSubcommand):
    """genspec sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(
            self, 'genspec', 'Generate a RPM spec file',
            ('Generate RPM spec files and fontconfig cofig files for PROJECT. '
             'If multiple assets is there, separate spec files will '
             'be generated.'))

    def do_register(self, parser: ArgumentParser) -> None:
        """Register arguments for sub-command."""
        parser.add_argument('-o',
                            '--outputdir',
                            default='.',
                            help='Output directory')
        parser.add_argument('--ignore-error',
                            nargs='*',
                            help='Deal with the specific error as warning')
        parser.add_argument('--build',
                            action='store_true',
                            help='Build RPM packages')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='Verbose operation')
        parser.add_argument('PROJECT', help='Project name')

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        noto = NotoRepos(self.token)
        releases = noto.get_releases(include=[args.PROJECT], all=False)
        if len(releases) == 0:
            m([': ']).info(args.PROJECT).error('Project not found.').out()
            sys.exit(1)
        if len(releases[args.PROJECT]) == 0:
            m([': ']).info(args.PROJECT).error('No releases.').out()
            sys.exit(1)
        for k, v in releases[args.PROJECT].items():
            assets = [
                i.browser_download_url for vv in v for i in list(vv.assets)
            ]
            for a in assets:
                fn = Path(urlparse(a).path).name
                if args.outputdir:
                    fn = str(Path(args.outputdir) / fn)
                if not Path(fn).exists():
                    if args.verbose:
                        m([' ']).message('Downloading from').info(a).out()
                    urlretrieve(a, fn)
            templates = gen.generate(
                k,
                assets,
                f'https://github.com/notofonts/{args.PROJECT}',
                # We need Epoch because the original google-noto-fonts'
                # versioning was based on date.
                epoch=1,
                common_description=(
                    'Noto is a collection of high-quality fonts with'
                    ' multiple weights and widths in sans, serif, mono'
                    ' and other styles, in more than 1,000 languages'
                    ' and over 150 writing systems.'),
                # Use fonts under googlefonts only.
                # 'full' may be better but this isn't necessarily available
                # for all the projects.
                # Dealing with full vs googlefonts per projects isn't
                # realistic.
                excludepath=['unhinted', 'hinted', 'full'],
                ignore_error=args.ignore_error)
            fe = sum(list(templates['fontconfig'][0]._families.values()),
                     [])[0]
            specname = Package.build_package_name('google', fe.family)
            fn = Path(args.outputdir) / (specname + '.spec')
            with open(fn, 'w') as f:
                f.write(templates['spec'])
            for fc in templates['fontconfig']:
                fc.path = args.outputdir
                fc.write()
            if args.build:
                self.build(specname, args.outputdir, args.outputdir)

    def build(self, id: str, sourcedir: str, outputdir: str) -> None:
        """Build RPM package."""
        specname = id + '.spec'
        rpmbuild = shutil.which('rpmbuild')
        if rpmbuild is None:
            m([': ']).error('rpmbuild not found.').throw(err.FileNotFoundError)
        p = Path(f'{outputdir}')
        srcdir = str(Path(f'{sourcedir}').resolve())
        builddir = str((p / 'BUILD').resolve())
        rpmdir = str((p / 'out').resolve())
        logfile = str((p / 'out' / f'build-{specname}.log').resolve())
        try:
            rpmbuild = subprocess.Popen([
                rpmbuild, '-ba', '--define', f'_specdir {srcdir}', '--define',
                f'_builddir {builddir}', '--define', f'_sourcedir {srcdir}',
                '--define', f'_srcrpmdir {rpmdir}', '--define',
                f'_rpmdir {rpmdir}', '--define',
                ('_rpmfilename %%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}'
                 '.%%{ARCH}.rpm'), specname
            ],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
            subprocess.check_call(('tee', logfile), stdin=rpmbuild.stdout)
            rpmbuild.communicate()
            m([' ']).message('Build finished with the exit code').info(
                rpmbuild.returncode).out()
        except subprocess.CalledProcessError:
            m().error('Buld failed.').throw(RuntimeError)
        finally:
            shutil.rmtree(builddir)


SUBCMD = [FnSubCmdGenSpec()]
