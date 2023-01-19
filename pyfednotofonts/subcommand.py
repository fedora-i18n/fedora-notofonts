# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Sub-commands abstract module."""

import glob
from argparse import ArgumentParser
from pathlib import Path


class FnSubcommand(object):
    """Sub-command class to represent."""

    _subcommands = {}

    @classmethod
    def load_subcommands(self):
        """Load all the sub-commands available."""
        cmds = []
        subdir = Path(__file__).parent
        files = [
            Path(f).stem
            for f in glob.glob(str(subdir / 'subcommands' / '*.py'))
        ]
        try:
            mods = __import__('subcommands', globals(), locals(), files, 0)
        except ImportError:
            mods = __import__('pyfednotofonts.subcommands', globals(),
                              locals(), files, 0)
        for m in [getattr(mods, f) for f in files]:
            cmds.extend(getattr(m, 'SUBCMD', []))
        for c in cmds:
            FnSubcommand._subcommands[c.info.command] = c

        return FnSubcommand._subcommands

    def __init__(self, cmd: str, helpstring: str):
        """Initialize sub-command."""
        self.info = FnSubcommandInfo(cmd, helpstring)
        self.token = None

    def register(self, parser: ArgumentParser) -> None:
        """Abstract function to register a sub-command."""
        self.do_register(parser)

    def do_register(self, parser: ArgumentParser) -> None:
        """Real function to register sub-command."""
        pass

    def set_token(self, token: str) -> None:
        """Set a GitHub token."""
        self.token = token


class FnSubcommandInfo(object):
    """Sub-command Information class."""

    def __init__(self, cmd: str, helpstring: str):
        """Initialize SubcommandInfo class."""
        self.command = cmd
        self.help_string = helpstring
