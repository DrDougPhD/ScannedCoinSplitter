#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib


class defaults(object):
    '''Default configuration for application
    '''
    # number of pixels to crop from the border of image
    scanner = "hpaio:/usb/Deskjet_F4100_series?serial=CN7CM6G1Q104TJ"
    # scanner = "genesys:libusb:001:015"
    border_reduction = 50
    intermediate_archival_directory = pathlib.Path('/tmp/scannedcoinsplitter/')
    minimum_coin_area = 22179
    cropped_output_directory = 'split'
    merged_output_directory = 'merged'
    output_directory = pathlib.Path('~').expanduser()/'Pictures'/'bullion'
    timeout = 60 #seconds, 1 minute