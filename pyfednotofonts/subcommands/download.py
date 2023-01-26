# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Download sub-command module."""

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
from pyfontrpmspec.messages import Message as m


class FnSubCmdDownload(FnSubcommand):
    """Download sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(
            self, 'download', 'Download a release',
            ('Download a release for PROJECT. if no release tag is set,'
             ' the latest assets will be used.'))

    def do_register(self, parser: ArgumentParser) -> None:
        """Register arguments for sub-command."""
        parser.add_argument('-t',
                            '--release-tag',
                            help='Release tag to download')
        parser.add_argument(
            '-o',
            '--output',
            default='.',
            help='Output directory to store downloaded archives')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='verbose operation')
        parser.add_argument('PROJECT', help='Project name')

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        noto = NotoRepos(self.token)
        releases = noto.get_releases(include=[args.PROJECT], all=True)
        if len(releases) == 0:
            m([': ']).info(args.PROJECT).error('Project not found.').out()
            sys.exit(1)
        if len(releases[args.PROJECT]) == 0:
            m([': ']).info(args.PROJECT).error('No releases.').out()
            sys.exit(1)
        if args.release_tag is not None:
            lr = [i for k, v in releases[args.PROJECT].items() for i in v]
            lr = list(filter(lambda x: x.title == args.release_tag, lr))
            if len(lr) == 0:
                m([': ', ' ']).info(args.release_tag).error(
                    'Release tag is not available in').info(
                        args.PROJECT).out()
                sys.exit(1)
        else:
            # If no release tag is presented, try to download the latest one.
            lr = []
            for k, v in releases[args.PROJECT].items():
                if len(v) > 1:
                    lr.append(
                        sorted(v, key=lambda x: x.comparable_version())[-1])
                else:
                    lr.extend(v)
        assets = sum([list(rel.assets) for rel in lr], [])
        if not args.verbose:
            m().info('This may take some time...').out()
        for a in assets:
            if args.verbose:
                m([' ']).message('Downloading from').info(
                    a.browser_download_url).out()
            fn = Path(urlparse(a.browser_download_url).path).name
            if args.output:
                fn = str(Path(args.output) / fn)
            urlretrieve(a.browser_download_url, fn)


SUBCMD = [FnSubCmdDownload()]
