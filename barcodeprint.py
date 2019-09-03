#!/usr/bin/env python3

import sys
import json
import subprocess
from tempfile import TemporaryFile as Tmp

config_file_path = 'streepjescode-printer.conf'

defaults = {
    '###': "'output' kan de speciale waarden 'stdout' of 'lpr' hebben",
    '## ': "anders wordt de waarde van 'output' als file naam opgevat",
    '#  ': '',
    'output':          '/tmp/streepjescodes.ps',   # "stdout", "lpr" of een file naam

    'page-size':       'A4',
    'unit':            'pt',

    'table-columns':   4,
    'table-lines':     10,
    'table-x-margin':  0,
    'table-y-margin':  0,

    'page-width':      None,
    'page-height':     None,
    'page-x-margin':   None,
    'page-y-margin':   None,

    'code-x-margin':   20,
    'code-y-margin':   20,
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
            print("Waarschuwing: {} bestaat niet.".format(config_file_path), file=sys.stderr)
            with open(config_file_path, 'x') as fdw:
                json.dump(self.config, fdw, indent=4)
                print(file=fdw)
            print("{} aangemaakt met default waarden.".format(config_file_path), file=sys.stderr)

    def printconfig(self):
        json.dump(self.config, sys.stdout, indent=4)

    def get_codes_per_page(self):
        num_codes_pp = self.config['table-columns'] * self.config['table-lines']
        return num_codes_pp

    def print(self, barcodes):
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
                '-p', pagesize,
                '-u', self.config['unit'],
                '-t', table,
        ]

        if self.config['output'] != 'stdout' and self.config['output'] != 'lpr':
            command.extend(('-o', self.config['output']))

        if geometry:
            command.append('-g {}'.format(geometry))
        if codemargin_x:
            command.append('-m')
            if codemargin_y:
                command.append('{},{}'.format(codemargin_x, codemargin_y))
            else:
                command.append(codemargin_x)

        if self.config['output'] == 'lpr':
            with Tmp() as postscript, Tmp() as stderr:
                proc1 = subprocess.Popen(
                            command,
                            stdin=subprocess.PIPE,
                            stdout=postscript,
                            stderr=stderr,
                            universal_newlines=True,
                        )
                result1 = proc1.communicate(input='\n'.join(barcodes))
                postscript.seek(0)

                proc2 = subprocess.Popen(
                            [ 'lpr' ],
                            stdin=postscript,
                            stderr=stderr,
                            universal_newlines=True,
                        )
                result2 = proc1.communicate()
                stderr.seek(0)
                error = stderr.read()
            return error
        else:
            result = subprocess.run(
                        command,
                        text=True,
                        input='\n'.join(barcodes),
                    )
            return result.stderr

    def printcommand(self, command):
        for arg in command:
            print(arg)

