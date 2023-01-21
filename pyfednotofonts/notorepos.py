# Copyright (C) 2023 fedora-notofonts Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Noto fonts GitHub repositories related code."""

import re
from github import Github
from packaging.version import parse
from typing import Any


class NotoRelease:
    """Container class for release."""

    def __init__(self, project, title, assets):
        """Initialize class."""
        self.project = project
        self.title = title
        matched = re.match(r'(.*)\-v(.*)', title)
        if matched is None:
            raise ValueError('Release tag is not like NAME-vVERSION style')
        self.name = matched.group(1)
        self.version = matched.group(2)
        self.assets = assets

    def comparable_version(self):
        """Return packaging.version.Version instance."""
        return parse(self.version)


class NotoRepos:
    """Operate gethering some information through GitHub REST API."""

    def __init__(self, token):
        """Initialize class."""
        self.github = Github(token)

    def get_releases(self,
                     **kwargs: Any) -> dict[str, dict[str, list[NotoRelease]]]:
        """Return a list of project names with releases.

        Currently following keyword arguments are supported:

        'all': bool - Retrieve all the releases available.
        'include': list[str] - a list of projects to retrieve.
        """
        excludelist = ['noto-fonts', 'noto-sans-nushu', 'test']
        all = kwargs['all'] if 'all' in kwargs else False
        include = kwargs['include'] if 'include' in kwargs else []

        retval = {}
        if len(include) == 0 or len(include) > 50:
            repos = self.github.get_organization('notofonts').get_repos(
                type='public')
        else:
            repos = [
                self.github.get_organization('notofonts').get_repo(n)
                for n in include
            ]
        for repo in repos:
            if repo.name in excludelist or repo.archived is True:
                continue
            if len(include) > 0 and repo.name not in include:
                continue
            releases = repo.get_releases()
            if releases is None or len(list(releases)) == 0:
                continue
            if repo.name not in retval:
                retval[repo.name] = {}
            for rel in releases:
                if rel is None:
                    continue
                ntr = NotoRelease(repo.name, rel.title, rel.get_assets())
                if ntr.name not in retval[repo.name]:
                    retval[repo.name][ntr.name] = []
                if all is True or len(retval[repo.name][ntr.name]) == 0:
                    retval[repo.name][ntr.name].append(ntr)
                else:
                    for i in retval[repo.name][ntr.name]:
                        if parse(i.version) < parse(ntr.version):
                            retval[repo.name][ntr.name][retval[repo.name][
                                ntr.name].index(i)] = ntr
        return retval
