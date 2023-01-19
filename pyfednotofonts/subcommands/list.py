# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""List sub-command module."""

from argparse import ArgumentParser
from github import Github
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand


class FnSubCmdList(FnSubcommand):
    """List sub-command class."""

    def __init__(self):
        """Initialize sub-command."""
        FnSubcommand.__init__(self, 'list', 'List available repo')

    def do_register(self, parser) -> None:
        """Register arguments for sub-command."""
        pass

    def handler(self, args: ArgumentParser) -> None:
        """Argument handler."""
        ignorelist = ['noto-fonts', 'noto-sans-nushu']
        g = Github(self.__token)
        for r in g.get_organization('notofonts').get_repos(type='public'):
            if r.name in ignorelist:
                continue
            if r.archived is not True:
                rel = None
                for rr in r.get_releases():
                    if rel is None or rel.published_at < rr.published_at:
                        rel = rr
                if rel is not None:
                    print('{}: {}'.format(r.name, rel.title))

    def do_set_token(self, token: str) -> None:
        """Set a GitHub token."""
        self.__token = token


SUBCMD = [FnSubCmdList()]
