#!/usr/bin/env python3

import sys
import json
import subprocess
from io import StringIO

config_file_path = 'barcode-printer.conf'

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
    def __init__(self):
        self.loadconfig()

    def loadconfig(self):
        self.config = defaults
        try:
            with open(config_file_path) as fdr:
                self.config.update(json.load(fdr))
        except FileNotFoundError:
            print("Waarschuwing: {} aangemaakt met default waarden.".format(config_file_path), file=sys.stderr)
            with open(config_file_path, 'x') as fdw:
                json.dump(self.config, fdw, sort_keys=True, indent=4)

    def printconfig(self):
        json.dump(self.config, sys.stdout, sort_keys=True, indent=4)

    def get_codes_per_page(self):
        num_codes_pp = self.config['table-columns'] * self.config['table-lines']
        return num_codes_pp

    def print(self, barcodes, ps_file_path=None):
        if not ps_file_path:
            ps_file_path = '/tmp/debug.ps'   # debug later gewoon pipe
        input_stream = StringIO('\n'.join(barcodes))

        pagesize = self.config['page-size']
        unit = self.config['unit']

        table = '{}x{}+{}+{}'.format(
                self.config['table-columns'],
                self.config['table-lines'],
                self.config['table-x-margin'],
                self.config['table-y-margin']
            )

        pagewidth = self.config['page-width']
        pageheight = self.config['page-height']
        pagemargin_x = self.config['page-x-margin']
        pagemargin_y = self.config['page-y-margin']

        geometry = ''
        if pagewidth and pageheight:
            geometry = '{}x{}'.format(pagewidth, pageheight)
        if pagemargin_x and pagemargin_y:
            geometry += '+{}+{}'.format(pagemargin_x, pagemargin_y)

        codemargin_x = self.config.get('code-x-margin')
        codemargin_y = self.config.get('code-y-margin')

        command = [
                'barcode',
                '-o', ps_file_path,
                '-p', pagesize,
                '-u', self.config['unit'],
                '-t', table,
        ]
        if geometry:
            command.append('-g {}'.format(geometry))
        if codemargin_x:
            command.append('-g')
            if codemargin_y:
                command.append('{},{}'.format(codemargin_x, codemargin_y))
            else:
                command.append(codemargin_x)

        self.printcommand(command)
#        result = subprocess.run(
#                )
#
        
    def printcommand(self, command):
        for arg in command:
            print(arg)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('Usage: {} [FILE]'.format(sys.argv[0]))
        sys.exit(exitcode)
    printer = BarcodePrinter()
    printer.printconfig()
    print()
    printer.print(['dummy1','dummy2'])

