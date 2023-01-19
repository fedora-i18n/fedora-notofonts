# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""List sub-command module."""

import re
from argparse import ArgumentParser
from github import Github
from packaging.version import Version, parse
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
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
        parser.add_argument('PROJECT', nargs='?', help='Project name')

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        excludelist = ['noto-fonts', 'noto-sans-nushu', 'test']
        nproj = 0
        nrel = 0
        g = Github(self.token)
        if args.PROJECT:
            repos = [g.get_organization('notofonts').get_repo(args.PROJECT)]
        else:
            repos = g.get_organization('notofonts').get_repos(type='public')
        for r in repos:
            if r.name in excludelist:
                continue
            if r.archived is not True:
                releases = []
                for rr in r.get_releases():
                    if rr is not None:
                        ma = re.match(r'(.*)\-v(.*)', rr.title)
                        if args.releases is True or len(releases) == 0:
                            releases.append(
                                FnReleaseInfo(ma.group(1), ma.group(2), rr))
                            nrel += 1
                        else:
                            a = list(
                                filter(lambda x: x.name == ma.group(1),
                                       releases))
                            if len(a) == 0:
                                releases.append(
                                    FnReleaseInfo(ma.group(1), ma.group(2),
                                                  rr))
                                nrel += 1
                            else:
                                for i in a:
                                    if i.version < parse(ma.group(2)):
                                        releases[releases.index(
                                            i)] = FnReleaseInfo(
                                                ma.group(1), ma.group(2), rr)
                if len(releases) > 0:
                    m([': ', '']).info(r.name).message(', '.join(
                        [r.obj.title for r in releases])).out()
                    nproj += 1
        m().message('').out()
        m([': ']).info('Project#').message(nproj).out()
        m([': ']).info('Release#').message(nrel).out()


class FnReleaseInfo:
    """Manage release information."""

    def __init__(self, name: str, version: str, obj: object):
        """Initialize the release information class."""
        self.name = name
        self.version = Version(version)
        self.obj = obj


SUBCMD = [FnSubCmdList()]
