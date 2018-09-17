#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the given images into individual coins/bars and merge corresponding
obverse and reverse images"""

import logging
import config
from .. import splitter

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
    obverse = splitter.extract_ingots(raw_scanned_image_path=args.obverse_image)
    reverse = splitter.extract_ingots(raw_scanned_image_path=args.reverse_image)

    merged_images = splitter.merge(
        obverse, reverse,
        config.defaults.merged_output_directory
    )
    logger.info("{0} merged images created".format(len(merged_images)))
    logger.info("\n".join(merged_images))
