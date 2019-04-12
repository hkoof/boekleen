#!/usr/bin/env python3
#
# Dit is het hoofdprogramma dat gedraaid moet worden om het
# programma "boekleen" te starten.
#
# De andere .py files worden in principe alleen (indirect) geimporteerd
# door dit python script.
#

import sys
import locale
import argparse
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

import prog
from boekleenDB import BoekLeenDB

from mainwindow import MainWindow

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        self.stop = False
        super().__init__(*args,
                application_id="hko.boekleen",
                **kwargs
            )

    def do_startup(self):
        Gtk.Application.do_startup(self)
        try:
            self.db = BoekLeenDB(self.db_path)
        except:
            print("Error opening database", self.db_path, file=sys.stderr)
            self.stop = True

    def do_activate(self):
        if not self.stop:
            self.window = MainWindow(application=self, title="Boekleen")
            self.window.show()

if __name__ == "__main__":
    try:
        locale.setlocale(locale.LC_ALL, "nl_NL.utf8")
    except locale.Error:
        print("Maak in uw besturingssysteem de locale 'nl_NL.utf8' beschikbaar"
              "voor datums en tijden in het nederlandse formaat.",
              file=sys.stderr
             )
    tabnamen = (
            "boek",
            "kastcode",
            "categorie",
            "lener",
            "uitlenen",
        )
    
    #### Command line parsing
    #
    parser = argparse.ArgumentParser(
            prog=prog.name,
            description=prog.description,
        )
    parser.add_argument(
            '-V', '--version',
            action='version',
            version='%(prog)s {}'.format(prog.version),
        )
#    parser.add_argument(
#            "-v", "--verbose",
#            action="store_true",
#            help="wollige proza",
#        )
    parser.add_argument(
            "--database",
            nargs='?',
            default=prog.default_sqlite_database_file,
            help="Pad naar de database file. Default: {}".format(prog.default_sqlite_database_file)
        )
    parser.add_argument(
            "--custom-isbn-prefix",
            nargs='?',
            default=None,
            help="Vaste eerste deel van eigen isbn code reeks",
        )
    parser.add_argument(
            "tabs",
            nargs='*',
            default="uitlenen",
            choices=tabnamen,
            help="Namen van tab's die zichtbaar moeten zijn. Default is alleen 'uitlenen'."
        )
    args = parser.parse_args()

    app = Application()
    if isinstance(args.tabs, str):
        args.tabs = (args.tabs,)
    app.tabs = list()
    for tab in args.tabs:
        if tab in app.tabs:
            print("Waarschuwing dubbele tab-naam:", tab, file=sys.stderr)
        else:
            app.tabs.append(tab)
    app.db_path = args.database
    app.custom_isbn_prefix = args.custom_isbn_prefix
    del args, parser
    app.run()

