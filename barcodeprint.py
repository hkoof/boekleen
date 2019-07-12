#!/usr/bin/env python3

import sys
import json
import subprocess
from io import StringIO

config_file_path = 'barcode-printer.conf'

defaults = {
    'page-size':       'A4',
    'unit':            'mm',

    'table-columns':   4,
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
        result = subprocess.run(
                command,
                stdin=input_stream,
                shell=True,
                capture_output=True,
                )

    def printcommand(self, command):
        for arg in command:
            print(arg)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('Usage: {} [FILE]'.format(sys.argv[0]))
        sys.exit(exitcode)
    printer = BarcodePrinter()
    print("codes per page:", printer.get_codes_per_page())
    #printer.printconfig()
    #print()

    printer.print([
        '9799999999990',
        '9799999999983',
        '9799999999976',
        '9799999999969',
        '9799999999952',
        '9799999999945',
        '9799999999938',
        '9799999999921',
        '9799999999914',
        '9799999999907',
        '9799999999891',
        '9799999999884',
        '9799999999877',
        '9799999999860',
        '9799999999853',
        '9799999999846',
        '9799999999839',
        '9799999999822',
        '9799999999815',
        '9799999999808',
        '9799999999792',
        '9799999999785',
        '9799999999778',
        '9799999999761',
        '9799999999754',
        '9799999999747',
        '9799999999730',
        '9799999999723',
        '9799999999716',
        '9799999999709',
        '9799999999693',
        '9799999999686',
        '9799999999679',
        '9799999999662',
        '9799999999655',
        '9799999999648',
        '9799999999631',
        '9799999999624',
        '9799999999617',
        '9799999999600',
        '9799999999594',
        '9799999999587',
        '9799999999570',
        '9799999999563',
        '9799999999556',
        '9799999999549',
        '9799999999532',
        '9799999999525',
        ])

