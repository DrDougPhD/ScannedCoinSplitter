#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import pathlib
import re
import sys


def main(args):
    scan_directory = pathlib.Path(args[1])
    print(f'Iterating over scanned and named images in {scan_directory}')

    ingots = []
    invalid_filenames = []
    for scanned_image in scan_directory.glob('merged/*.png'):
        try:
            ingot = Ingot(path=scanned_image)
        except AttributeError:
            invalid_filenames.append(scanned_image)
        else:
            print('.'*80)
            print(ingot)
            print(f'\tname   := {ingot.name}')
            print(f'\tweight := {ingot.weight}')
            ingots.append(ingot)

    with Inventory(scan_directory=scan_directory) as inventory:
        for ingot in ingots:
            inventory.add(ingot=ingot)

    if len(invalid_filenames) > 0:
        print('!'*80)
        print(f'{len(invalid_filenames)} invalid filenames:')
        for path in invalid_filenames:
            print(f'\t{path}')
        print('Aborting.')
        sys.exit(1)


class WeightParser(object):
    weight_regex = re.compile(r'.+(?P<value>\d+) (?P<unit>ozt|g).+')

    weight_converter = {
        'g': lambda v: v / 31.1,
        'ozt': lambda v: v,
    }

    def __init__(self, filename: str):
        parsed_weight = self.weight_regex.match(filename).groupdict()
        self.raw = parsed_weight['value']
        self.value = float(self.raw)
        if self.value.is_integer():
            self.value = int(self.value)

        self.unit = parsed_weight['unit']

    def to_ozt(self):
        return self.weight_converter[self.unit](self.value)

    def __repr__(self):
        return f'{self.raw} {self.unit}'


class IngotNameParser(object):
    def __init__(self, path: pathlib.Path, weight: WeightParser):
        self.name = path.stem.replace(str(weight), '').strip()

    def __repr__(self):
        return self.name


class Ingot(object):
    def __init__(self, path: pathlib.Path):
        self.filename = path.name
        self.weight = WeightParser(filename=self.filename)
        self.name = IngotNameParser(path=path, weight=self.weight)

    def __repr__(self):
        return self.filename


class Inventory(object):
    fieldnames = [
        'item',
        'qty',
        'ozt',
        'g',
    ]

    def __init__(self, scan_directory: pathlib.Path):
        self.filename = f'{scan_directory.name}.csv'
        self.csv_file = open(self.filename, 'w')
        self.csv_writer = csv.DictWriter(self.csv_file,
                                         fieldnames=self.fieldnames)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.csv_file.close()

    def add(self, ingot: Ingot):
        self.csv_writer.writerow({
            'item': str(ingot.name),
            'qty': 1,
            'ozt': ingot.weight.raw if ingot.weight.unit == 'ozt' else '',
            'g': ingot.weight.raw if ingot.weight.unit == 'g' else '',
        })


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} PATH/TO/NAMED/SCANS/DIRECTORY')
        sys.exit(1)

    main(sys.argv)