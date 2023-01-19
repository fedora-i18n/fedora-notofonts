# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""GitHub-related sub-command module."""

import re
import sys
import urllib.request
import urllib.parse
from argparse import ArgumentParser
from github import Github
from packaging.version import Version, parse
from pathlib import Path
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
from pyfontrpmspec.messages import Message as m


class FnReleaseInfo:
    """Manage release information."""

    def __init__(self, name: str, version: str, obj: object):
        """Initialize the release information class."""
        self.name = name
        self.version = version
        self.obj = obj


def get_latest_releases(repo, all=False) -> list[FnReleaseInfo]:
    """Return the latest releases from GitHub."""
    releases = []
    for rr in repo.get_releases():
        if rr is not None:
            ma = re.match(r'(.*)\-v(.*)', rr.title)
            if all is True or len(releases) == 0:
                releases.append(FnReleaseInfo(ma.group(1), ma.group(2), rr))
            else:
                a = list(filter(lambda x: x.name == ma.group(1), releases))
                if len(a) == 0:
                    releases.append(FnReleaseInfo(ma.group(1), ma.group(2),
                                                  rr))
                else:
                    for i in a:
                        if Version(i.version) < parse(ma.group(2)):
                            releases[releases.index(i)] = FnReleaseInfo(
                                ma.group(1), ma.group(2), rr)
    return releases


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
                releases = get_latest_releases(r, args.releases)
                nrel += len(releases)
                if len(releases) > 0:
                    m([': ', '']).info(r.name).message(', '.join(
                        [r.obj.title for r in releases])).out()
                    nproj += 1
        m().message('').out()
        m([': ']).info('Project#').message(nproj).out()
        m([': ']).info('Release#').message(nrel).out()


class FnSubCmdDownload(FnSubcommand):
    """Download sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(self, 'download', 'Download a release')

    def do_register(self, parser: ArgumentParser) -> None:
        """Register arguments for sub-command."""
        parser.add_argument('-t',
                            '--release-tag',
                            help='Release tag to download')
        parser.add_argument(
            '-o',
            '--output',
            help='Output directory to store downloaded archives')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='verbose operation')
        parser.add_argument('PROJECT', help='Project name')

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        g = Github(self.token)
        repo = g.get_organization('notofonts').get_repo(args.PROJECT)
        if repo is None:
            m([': ']).error(args.PROJECT).message('Project not found.').out()
            sys.exit(1)
        releases = get_latest_releases(repo, False)
        if args.release_tag is not None:
            releases = list(
                filter(
                    lambda x: '{}-v{}'.format(x.name, x.version) == args.
                    release_tag, releases))
            if len(releases) == 0:
                m([': ', ' ']).error(args.release_tag).message(
                    'Release tag is not available in').info(
                        args.PROJECT).out()
                sys.exit(1)
        assets = sum([list(rel.obj.get_assets()) for rel in releases], [])
        for a in assets:
            if args.verbose:
                m([' ']).message('Downloading from').info(
                    a.browser_download_url).out()
            fn = Path(urllib.parse.urlparse(a.browser_download_url).path).name
            if args.output:
                fn = str(Path(args.output) / fn)
            urllib.request.urlretrieve(a.browser_download_url, fn)


SUBCMD = [FnSubCmdList(), FnSubCmdDownload()]
