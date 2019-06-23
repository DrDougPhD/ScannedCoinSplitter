#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import termcolor


class MissingScannerException(Exception):
    def __init__(self, scanner_uri):
        self.message = 'Scanner missing! Cannot find {scanner}'.format(
            scanner=termcolor.colored(scanner_uri, 'yellow', attrs=['bold'])
        )
