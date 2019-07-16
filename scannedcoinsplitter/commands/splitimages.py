#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the given images into individual coins/bars and merge corresponding
obverse and reverse images"""

import logging
import pathlib

import config
from .. import splitter

logger = logging.getLogger(__name__)


def cli(subcommand):
    '''Add command-line arguments to this subcommand
    '''
    subcommand.add_argument(
        '-f', '--obverse-image',
        help='input obverse image',
    )
    subcommand.add_argument(
        '-b', '--reverse-image',
        help='input reverse image',
    )
    subcommand.add_argument(
        '-o', '--output-directory',
        help='directory into which to output scans',
        default=config.defaults.output_directory,
        type=pathlib.Path
    )
    subcommand.set_defaults(func=main)


def main(args):
    cropped_output_directory = args.output_directory / config.defaults.cropped_output_directory
    cropped_output_directory.mkdir(parents=True, exist_ok=True)

    merged_output_directory = args.output_directory / config.defaults.merged_output_directory
    merged_output_directory.mkdir(parents=True, exist_ok=True)

    # open obverse and reverse images
    obverse = splitter.extract_ingots(raw_scanned_image_path=args.obverse_image,
                                      output_directory=cropped_output_directory)
    reverse = splitter.extract_ingots(raw_scanned_image_path=args.reverse_image,
                                      output_directory=cropped_output_directory)

    merged_images = splitter.merge(
        obverse, reverse,
        merged_output_directory
    )
    logger.info("{0} merged images created".format(len(merged_images)))
    logger.info("\n".join(merged_images))
