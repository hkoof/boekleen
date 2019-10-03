import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from datetime import datetime

from datalijst import DataLijst, ColumnDef
from uitleendialog import UitleenDialog

class UitleenWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.invalidated = True
        self.lener = None

        self.barcode = Gtk.Entry()
        #self.barcode.set_can_focus(False)
        self.handmatig_isbn = Gtk.Button("Zoek code")
        self.handmatig_isbn.connect("clicked", self.on_handmatig_clicked)

        self.vandaag_radio = Gtk.RadioButton.new_with_label_from_widget(
                None,
                "Vandaag uitgeleend"
            )
        self.vandaag_radio.connect("toggled", self.refresh)

        self.een_week_radio = Gtk.RadioButton.new_with_label_from_widget(
                self.vandaag_radio,
                "1 week of langer in uitleen"
            )
        self.een_week_radio.connect("toggled", self.refresh)

        self.jaar_radio = Gtk.RadioButton.new_with_label_from_widget(
                self.vandaag_radio,
                "1 jaar of langer in uitleen"
            )
        self.jaar_radio.connect("toggled", self.refresh)

        self.nu_uitgeleend_radio = Gtk.RadioButton.new_with_label_from_widget(
                self.vandaag_radio,
                "Alles nu in uitleen"
            )
        self.nu_uitgeleend_radio.connect("toggled", self.refresh)

        self.logview = Gtk.TextView(hexpand=True)
        self.logview.set_can_focus(False)
        self.logview.set_editable(False)
        self.logview.set_cursor_visible(False)
        self.logbuffer = self.logview.get_buffer()

        columns = (
            ColumnDef("Titel", "titel"),
            ColumnDef("Auteur", "auteur"),
            ColumnDef("Voornaam", "voornaam"),
            ColumnDef("Achternaam", "achternaam"),
            ColumnDef("Klas", "klas"),
            #ColumnDef("Uitgeleend", "uitgeleend", datatype=str),
            ColumnDef("Leendagen", "leendagen", datatype=int),
        )
        self.leenlijst = DataLijst(columns, show_primary_key=True, expand=True)

        # Layout
        #
        barcode_grid = Gtk.Grid(
                margin=8,
                column_spacing=4,
                row_spacing=4,
                orientation=Gtk.Orientation.VERTICAL
            )
        barcode_grid.add(self.barcode)
        barcode_grid.add(self.handmatig_isbn)
        barcode_grid.add(Gtk.Label())
        barcode_paneel = Gtk.Frame(label="Streepjescode")
        barcode_paneel.add(barcode_grid)

        radio_grid = Gtk.Grid(
                margin=8,
                column_spacing=4,
                row_spacing=4,
                orientation=Gtk.Orientation.VERTICAL
            )
        radio_grid.add(self.vandaag_radio)
        radio_grid.add(self.een_week_radio)
        radio_grid.add(self.jaar_radio)
        radio_grid.add(self.nu_uitgeleend_radio)
        radio_paneel = Gtk.Frame(label="Selectie")
        radio_paneel.add(radio_grid)

        scrolled_logview = Gtk.ScrolledWindow(margin=4)
        scrolled_logview.add(self.logview)
        log_paneel = Gtk.Frame(label="Log")
        log_paneel.add(scrolled_logview)

        paneel = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
                hexpand=True,
                #halign=Gtk.Align.START,
            )
        paneel.attach(barcode_paneel, 0, 0, 1, 1)
        paneel.attach(radio_paneel, 1, 0, 1, 1)
        #paneel.attach(Gtk.Label(hexpand=True), 2, 0, 1, 1)
        paneel.attach(log_paneel, 2, 0, 2, 1)

        self.add(paneel)
        self.add(self.leenlijst)

    def refresh(self, sender=None):
        # Don't double refresh. The radiobutton that loses being "on" als send the signal
        if isinstance(sender, Gtk.RadioButton) and not sender.get_active():
            return
        if self.vandaag_radio.get_active():
            data = self.db.uitleningen(uitgeleend=True, max_dagen_uitgeleend=0)
        elif self.een_week_radio.get_active():
            data = self.db.uitleningen(uitgeleend=True, min_dagen_uitgeleend=7)
        elif self.jaar_radio.get_active():
            data = self.db.uitleningen(uitgeleend=True, min_dagen_uitgeleend=365)
        elif self.nu_uitgeleend_radio.get_active():
            data = self.db.uitleningen(uitgeleend=True)
        else:
            print ("error: onbekende uitlening")
            # Should never happen: radiobutton aanwezig die hier niet behandled wordt
        self.leenlijst.load(data)
        self.invalidated = False

    def leenlog(self, pangotext):
        where = self.logbuffer.get_start_iter()
        now = datetime.now().strftime("%H:%M:%S")
        pangotext = "{} {}\n".format(now, pangotext)
        self.logbuffer.insert_markup(where, pangotext, -1)
        self.logview.scroll_to_iter(where, 0.0, False, 0.0, 0.0)

    def on_handmatig_clicked(self, button):
        isbn = self.barcode.get_text()
        self.on_isbn_scan(isbn)

    def on_isbn_scan(self, isbn):
        self.barcode.set_text(isbn)
        boek = self.db.boeken(isbn)
        if not boek:
            message = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Boek is niet bekend in het bestand"
            )
            response = message.run()
            message.destroy()
            return
        verwijderd = boek['verwijdertijdstip']
        if verwijderd:
            tijdstip = datetime.fromtimestamp(verwijderd)
            message = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Boek is verwijderd op {}".format(
                    tijdstip.strftime('%A %w %B %Y om %X')
                )
            )
            response = message.run()
            message.destroy()
            return
        uitlening = self.db.uitgeleend(isbn)
        if uitlening:
            self.db.brengterug(isbn)
            self.refresh()
            self.leenlog('<span foreground="green" size="x-large"><b>←</b></span> {} {} brengt <i>"{}"</i> terug'.format(
                    uitlening['voornaam'],
                    uitlening['achternaam'],
                    uitlening['titel'],
                ))
        else:
            dialog = UitleenDialog(self.parent, self.db, boek, self.lener)
            response = dialog.run()
            if response == 1:  # custom response: default lener
                self.lener = dialog.default_lener
            if response == Gtk.ResponseType.OK:
                self.lener = dialog.get_lener()
            if response == 1 or response == Gtk.ResponseType.OK:
                lener = self.db.persoon(self.lener)
                if not lener:
                    print("error: onbekende lener: {}".format(self.lener))
                else:
                    self.db.leenuit(self.lener, isbn)
                    self.leenlog('<span foreground="blue" size="x-large"><b>→</b></span> {} {} leent <i>"{}"</i>'.format(
                            lener['voornaam'],
                            lener['achternaam'],
                            boek['titel'],
                        ))
                self.refresh()
            dialog.destroy()
        self.parent.invalidate()
