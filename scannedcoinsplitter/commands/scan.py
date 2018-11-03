#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the given images into individual coins/bars and merge corresponding
obverse and reverse images"""
import datetime
import logging
import subprocess
import pathlib

import termcolor

logger = logging.getLogger(__name__)

import config
from .. import splitter


def cli(subcommand):
    '''Add command-line arguments to this subcommand
    '''
    subcommand.add_argument(
        '-o', '--output-directory',
        help='directory into which to output scans',
        default=config.defaults.output_directory,
        type=pathlib.Path
    )
    subcommand.add_argument(
        '-n', '--image-name',
        help='name to give scans',
        default=datetime.datetime.today().strftime('%Y-%m-%d')
    )
    subcommand.set_defaults(func=main)


def main(args):
    # create output directory if it doesn't exist
    args.output_directory.mkdir(parents=True, exist_ok=True)

    # find a unique name for this image
    filename_template = '{name} - {number_field} - obverse.tiff'.format(
        name=args.image_name,
        number_field='{index}',
    )
    obverse_image_file_path = generate_unique_filename(
        directory=args.output_directory,
        filename_template=filename_template,
        field_name='index'
    )

    # begin scan of obverse image
    obverse = start_scan(path=obverse_image_file_path)

    # wait for the user to flip the coins/bars on the scanner
    input('Press Enter after flipping coins/bars on scanner...')

    reverse_image_file_path = args.output_directory/obverse.name.replace(
        'obverse', 'reverse'
    )
    reverse = start_scan(path=reverse_image_file_path)

    obverse = splitter.extract_ingots(raw_scanned_image_path=obverse)
    reverse = splitter.extract_ingots(raw_scanned_image_path=reverse)

    merged_images = splitter.merge(
        obverse, reverse,
        config.defaults.merged_output_directory
    )
    logger.info("{0} merged images created".format(len(merged_images)))
    logger.info("\n".join(merged_images))


def start_scan(path):
    logger.info('Beginning scan')
    with open(str(path), 'w') as scanned_file:
        subprocess.call([
            "scanimage",
            "--device-name", config.defaults.scanner,
            # "--device", config.defaults.scanner,
            "--resolution", "300",
            "--format=tiff",
        ], stdout=scanned_file)

    logger.info('Scanning complete: {file}'.format(
        file=termcolor.colored(path, 'green', attrs=['bold'])
    ))

    return path


def generate_unique_filename(directory, filename_template, field_name):
    index = 0
    while True: # increment until a file of the given template is not found
        filename = filename_template.format(**{field_name: index})

        if not (directory / filename).is_file():
            break

        else:
            index += 1

    logger.debug('Unique filename found: {filename}'.format(
        filename=termcolor.colored(filename, 'cyan')
    ))
    return directory/filename
