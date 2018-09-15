#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	python splitter.py [-h,--help] [-v,--verbose]


DESCRIPTION

	Concisely describe the purpose this script serves.


ARGUMENTS

	-h, --help          show this help message and exit
	-v, --verbose       verbose output


AUTHOR

	Doug McGeehan


LICENSE

	Copyright 2018 Doug McGeehan - GNU GPLv3

"""
import logging
import progressbar

import cli


__appname__ = "scannedcoinsplitter"
__author__ = "Doug McGeehan"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"
__indevelopment__ = True        # change this to false when releases are ready


progressbar.streams.wrap_stderr()
logger = logging.getLogger('scannedcoinsplitter')


def main(args):
    '''ADD DESCRIPTION HERE'''
    args.func(args=args)


if __name__ == '__main__':
    with cli.prepare(app='scannedcoinsplitter',
                     description=main.__doc__,
                     verbosity=__indevelopment__) as commandline:
        main(args=commandline.arguments)
