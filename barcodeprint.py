#!/usr/bin/env python3

import sys
import json
import subprocess
from cStringIO import StringIO

default_config_file_path = 'barcode-printer.conf'

defaults = {
    'page-size':       'A4',
    'unit':            'mm',

    'table-columns':   5,
    'table-lines':     12,
    'table-x-margin':  0,
    'table-y-margin':  0,

    'page-width':      None,
    'page-height':     None,
    'page-x-margin':   None,
    'page-y-margin':   None,

    'code-x-margin':   None,
    'code-y-margin':   None,
    }

class BarcodePrinter:
    def __init__(self, config_file_path=None):
        if config_file_path:
            self.load(config_file_path)

    def load(self, config_file_path=default_config_file_path):
        self.config = dict(defaults)
        with open(config_file_path) as fd:
            self.config.update(json.load(fd))

    def print(self, barcodes, ps_file_path=None):
        if not ps_file_path:
            ps_file_path = '/tmp/debug.ps'   # debug later gewoon pipe
        input_stream = StringIO('\n'.join(barcodes))
        pagewidth = self.config['page-width']
        pageheight = self.config['pageheight']
        pagemargin_x = self.config['page-x-margin']
        pagemargin_y = self.config['page-y-margin']

        geometry = ''
        if pagewidth and pageheight:
            geometry = '{}x{}'.format(pagewidth, pageheight)
        if pagemargin_x and pagemargin_y:
            geometry += '+{}+{}'.format(pagemargin_x, pagemargin_y)

        table = '{}x{}+{}+{}'.format(
                self.config['table-columns'],
                self.config['table-lines'],
                self.config['table-x-margin'],
                self.config['table-y-margin']
            )

        if self.config['code-x-margin']:

        command = [
                'barcode',
                '-o {}', ps_file_path,
                '-u' + self.config['unit']),
                '-t' + table,
                '-m'
        ]
        if geometry:
            command.append('-g {}'.format(geometry))
        result = subprocess.run(
                )

if __name__ == '__main__':
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

