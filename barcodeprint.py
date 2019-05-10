#!/usr/bin/env python3

import sys
import json

default_config_file_path = 'barcode-printer.conf'

defaults = {
    'page-size':       'A4',
    'unit':            'mm',

    'page-width':      None,
    'page-height':     None,
    'page-x-margin':   None,
    'page-y-margin':   None,

    'table-columns':   5,
    'table-lines':     12,
    'table-x-margin':  0,
    'table-x-margin':  0,
    }

class BarcodePrinter:
    def __init__(self, config_file_path=default_config_file_path):
        self.config = dict(defaults)
        with open(config_file_path) as fd:
            self.config.update(json.load(fd))


if __name__ == "__main__":
    config_file_path = default_config_file_path
    nargs = len(sys.argv)

    if nargs == 2:
        config_file_path = sys.argv[1]
    elif nargs > 2:
        print('Usage: {} [FILE]'.format(sys.argv[0]))
        sys.exit(1)

    try:
        with open(config_file_path, 'x') as fd:
            json.dump(defaults, fd, sort_keys=True, indent=4)
            print(file=fd)  # extra newline
    except FileExistsError:
        print('Error: {} already exists'.format(config_file_path), file=sys.stderr)
        sys.exit(1)

