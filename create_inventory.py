#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib
import re
import sys


def main(args):
    scan_directory = pathlib.Path(args[1])
    print(f'Iterating over scanned and named images in {scan_directory}')

    for scanned_image in scan_directory.glob('merged/*.png'):
        try:
            ingot = Ingot(path=scanned_image)
        except AttributeError:
            continue
        else:
            print('.'*80)
            print(ingot)
            print(f'\tname   := {ingot.name}')
            print(f'\tweight := {ingot.weight}')


class WeightParser(object):
    weight_regex = re.compile(r'.+(?P<value>\d+) (?P<unit>ozt|g).+')

    weight_converter = {
        'g': lambda v: v / 31.1,
        'ozt': lambda v: v,
    }

    def __init__(self, filename: str):
        parsed_weight = self.weight_regex.match(filename).groupdict()
        self.weight_str = parsed_weight['value']
        self.weight = float(self.weight_str)
        if self.weight.is_integer():
            self.weight = int(self.weight)

        self.unit = parsed_weight['unit']

    def to_ozt(self):
        return self.weight_converter[self.unit](self.weight)

    def __repr__(self):
        return f'{self.weight_str} {self.unit}'


class IngotNameParser(object):
    def __init__(self, path: pathlib.Path, weight: WeightParser):
        self.name = path.stem.replace(str(weight), '')

    def __repr__(self):
        return self.name


class Ingot(object):
    def __init__(self, path: pathlib.Path):
        self.filename = path.name
        self.weight = WeightParser(filename=self.filename)
        self.name = IngotNameParser(path=path, weight=self.weight)

    def __repr__(self):
        return self.filename


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} PATH/TO/NAMED/SCANS/DIRECTORY')
        sys.exit(1)

    main(sys.argv)