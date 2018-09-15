#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the given images into individual coins/bars and merge corresponding
obverse and reverse images"""

import logging

logger = logging.getLogger(__name__)


def cli(subcommand):
    '''Add command-line arguments to this subcommand
    '''
    subcommand.add_argument(
        '-o', '--obverse-image',
        help='input obverse image',
    )
    subcommand.add_argument(
        '-r', '--reverse-image',
        help='input reverse image',
    )
    subcommand.set_defaults(func=main)


def main(args):
    # open obverse and reverse images
    pass
