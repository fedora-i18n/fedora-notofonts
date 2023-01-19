# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Module to package Noto Fonts from github."""

import argparse
import sys
try:
    from subcommand import FnSubcommand
except ImportError:
    from pyfednotofonts.subcommand import FnSubcommand
from pyfontrpmspec.messages import Message as m
from xdg import xdg_config_home


def main():
    """Endpoint function to package Noto Fonts from github."""
    configfile = xdg_config_home() / '.fedora-notofonts'
    if configfile.exists() is not True:
        m([': ']).error(str(configfile)).message(
            ('file not found. Please create API token from '
             'https://github.com/settings/tokens '
             'and put your token into a file as it is.')).out()
        m([': ', ',']).message('Required scope is').info('public_repo').info(
            'read:packages').info('read:project').out()
        sys.exit(1)

    token = configfile.read_text().rstrip()

    parser = argparse.ArgumentParser(
        description='Noto Fonts packaging helper',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subcmds = FnSubcommand.load_subcommands()
    subparsers = parser.add_subparsers()
    for x in sorted(subcmds.keys()):
        pp = subparsers.add_parser(subcmds[x].info.command,
                                   help=subcmds[x].info.help_string)
        subcmds[x].register(pp)
        subcmds[x].set_token(token)
        pp.set_defaults(handler=subcmds[x].handler)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
