#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib


class defaults(object):
    '''Default configuration for application
    '''
    # number of pixels to crop from the border of image
    border_reduction = 50
    intermediate_archival_directory = pathlib.Path('/tmp/scannedcoinsplitter/')
    minimum_coin_area = 22179
    cropped_output_directory = './results/cropped'
    merged_output_directory = './results/merged'
    output_directory = pathlib.Path('~').expanduser()/'Pictures'/'bullion'