# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""List sub-command module."""

from argparse import ArgumentParser
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
try:
    from notorepos import NotoRepos
except ImportError:
    from pyfednotofonts.notorepos import NotoRepos
from pyfontrpmspec.messages import Message as m


class FnSubCmdList(FnSubcommand):
    """List sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(self, 'list', 'List available repo')

    def do_register(self, parser: ArgumentParser) -> None:
        """Register arguments for sub-command."""
        parser.add_argument('-r',
                            '--releases',
                            action='store_true',
                            help='List all the releases')
        parser.add_argument('PROJECT', nargs='*', help='Project name')

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        nproj = 0
        nrel = 0
        noto = NotoRepos(self.token)
        projects = None
        if args.PROJECT:
            projects = args.PROJECT
        else:
            projects = []
        if len(projects) == 0 or len(projects) > 50:
            m().message('This may take a while...').out()
        releases = noto.get_releases(include=projects, all=args.releases)
        nproj = len(releases)
        nrel = sum([len(xx) for x in releases.values() for xx in x.values()])

        if nproj > 0:
            for k, v in releases.items():
                lr = []
                if v is not None:
                    lr = [
                        i.title for kk, vv in releases[k].items() for i in vv
                    ]
                m([': ', '']).info(k).message(', '.join(lr)).out()
        m().message('').out()
        m([': ']).info('Project#').message(nproj).out()
        m([': ']).info('Release#').message(nrel).out()


SUBCMD = [FnSubCmdList()]
