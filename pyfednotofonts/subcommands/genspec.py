# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Genspec sub-command module."""

import sys
from argparse import ArgumentParser
from pathlib import Path
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
try:
    from notorepos import NotoRepos
except ImportError:
    from pyfednotofonts.notorepos import NotoRepos
import pyfontrpmspec.generator as gen
from pyfontrpmspec.messages import Message as m
from pyfontrpmspec.package import Package


class FnSubCmdGenSpec(FnSubcommand):
    """genspec sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(self, 'genspec', 'Generate a RPM spec file')

    def do_register(self, parser: ArgumentParser) -> None:
        """Register arguments for sub-command."""
        parser.add_argument('-o',
                            '--outputdir',
                            default='.',
                            help='Output directory')
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
            templates = gen.generate(
                k,
                [i.browser_download_url for vv in v for i in list(vv.assets)],
                f'https://github.com/notofonts/{args.PROJECT}',
                excludepath=['unhinted', 'hinted', 'googlefonts'])
            fe = sum(list(templates['fontconfig'][0]._families.values()),
                     [])[0]
            specname = Package.build_package_name('google', fe.family)
            fn = Path(args.outputdir) / (specname + '.spec')
            with open(fn, 'w') as f:
                f.write(templates['spec'])
            for fc in templates['fontconfig']:
                fc.path = args.outputdir
                fc.write()


SUBCMD = [FnSubCmdGenSpec()]
