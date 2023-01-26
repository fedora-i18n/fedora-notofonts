# fedora-notofonts
[![pip version badge](https://img.shields.io/pypi/v/fedora-notofonts)](https://pypi.org/project/fedora-notofonts/)
[![tag badge](https://img.shields.io/github/v/tag/fedora-i18n/fedora-notofonts)](https://github.com/fedora-i18n/fedora-notofonts/tags)
[![license badge](https://img.shields.io/github/license/fedora-i18n/fedora-notofonts)](./LICENSE)

Helper tools to package Noto Fonts for Fedora

## Setup

``` shell
$ pip3 install build
$ python3 -m build
$ pip3 install --user dist/fedora-notofonts*.whl
```

## Usage

``` shell
usage: frondend.py [-h] {download,genspec,list} ...

Noto Fonts packaging helper

positional arguments:
  {download,genspec,list}
    download            Download a release
    genspec             Generate a RPM spec file
    list                List available repo

options:
  -h, --help            show this help message and exit
```
