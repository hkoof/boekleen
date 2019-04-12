import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from persoonwidget import PersoonWidget

class UitleenDialog(Gtk.Dialog):
    def __init__(self, parent, database, boek):
        super().__init__(
                "Uitlenen: '{}'".format(boek['titel']),
                parent,
                Gtk.DialogFlags.MODAL,
            )
        self.set_default_response(Gtk.ResponseType.OK)
        self.db = database

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL).set_can_focus(False)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        boeklabel = Gtk.Label('<big><b>"{}"</b></big>  -  <big>{}</big>'.format(
                boek['titel'],
                boek['auteur'],
            )
        )
        boeklabel.set_use_markup(True)

        self.lenerswidget = PersoonWidget(self, database, read_only=True)

        # Layout
        #
        grid = Gtk.Grid(
                row_spacing=8,
                column_spacing=8,
                margin=8,
            )
        grid.attach(boeklabel, 0, 0, 1, 1)
        grid.attach(self.lenerswidget, 0, 1, 1, 1)
        self.get_content_area().add(grid)
        self.set_default_size(640, 500)

        personen = self.db.alle_personen()
        self.lenerswidget.lijst.load(personen)
        self.show_all()

    def get_lener(self):
        persoon_id = self.lenerswidget.lijst.get_selected()
        return persoon_id

