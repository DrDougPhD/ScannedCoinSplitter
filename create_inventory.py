#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib
import sys


def main(args):
    scan_directory = pathlib.Path(args[1])
    print(f'Iterating over scanned and named images in {scan_directory}')

    for scanned_image in scan_directory.glob('merged/*.png'):
        print(f'\t{scanned_image}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} PATH/TO/NAMED/SCANS/DIRECTORY')
        sys.exit(1)

    main(sys.argv)