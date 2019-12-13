import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from persoonwidget import PersoonWidget

class UitleenDialog(Gtk.Dialog):
    def __init__(self, parent, database, boek=None, lener=None):
        super().__init__("Uitlenen", parent, Gtk.DialogFlags.MODAL)
        self.set_default_response(Gtk.ResponseType.OK)
        self.db = database
        self.default_lener = None

        self.default_lener_button = self.add_button('...', 1)
        self.default_lener_button.set_sensitive(False)
        self.button_cancel = self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL).set_can_focus(False)
        self.button_OK = self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.button_OK.set_sensitive(False)

        self.set_default_response(Gtk.ResponseType.OK)

        self.boeklabel = Gtk.Label()
        self.lenerswidget = PersoonWidget(self, database, read_only=True)
        self.selection = self.lenerswidget.lijst.lijst.view.get_selection()
        self.selection.connect("changed", self.on_select_row)

        # Layout
        #
        grid = Gtk.Grid(
                row_spacing=8,
                column_spacing=8,
                margin=8,
            )
        grid.attach(self.boeklabel, 0, 0, 1, 1)
        grid.attach(self.lenerswidget, 0, 1, 1, 1)
        self.get_content_area().add(grid)
        self.set_default_size(640, 500)

        personen = self.db.alle_personen()
        self.lenerswidget.lijst.load(personen)
        if boek:
            self.set_boek(boek)
        if lener:
            self.set_default_lener(lener)
        self.show_all()

    def set_default_lener(self, lener_id):
        self.default_lener = lener_id
        lener = self.db.persoon(lener_id)
        lener_naam = "{} {}".format(lener['voornaam'], lener['achternaam'])
        button_tekst = "Vorige lener weer kiezen:\n<b>{}</b>".format(lener_naam)
        for bchild in self.default_lener_button.get_children():
            bchild.set_label(button_tekst)
            bchild.set_use_markup(True)

        self.default_lener_button.set_sensitive(True)
        # self.set_default_response(1) # commented: barcode scanner verzend een 'enter'. Dit geeft fouten.

    def get_lener(self):
        persoon_id = self.lenerswidget.lijst.get_selected()
        return persoon_id

    def set_boek(self, boek):
        self.set_title("Uitlenen: '{}'".format(boek['titel']))
        self.boeklabel.set_text('<big><b>"{}"</b></big>  -  <big>{}</big>'.format(
                boek['titel'],
                boek['auteur'],
            )
        )
        self.boeklabel.set_use_markup(True)

    def on_select_row(self, view):
        if self.lenerswidget.lijst.get_selected():
            self.button_OK.set_sensitive(True)
        else:
            self.button_OK.set_sensitive(False)


    def on_row_activated(self, view, path, column):
        self.response(Gtk.ResponseType.OK)
