import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TerugbrengDialog(Gtk.Dialog):
    def __init__(self, parent, uitlening):
        super().__init__(
                "Terugbrengen: '{}'".format(uitlening['titel']),
                parent,
                Gtk.DialogFlags.MODAL,
            )
        self.set_default_response(Gtk.ResponseType.OK)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL).set_can_focus(False)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK).set_can_focus(False)

        lenerlabel = Gtk.Label("<big><b>{} {}</b> brengt terug:</big>".format(
                uitlening['voornaam'],
                uitlening['achternaam']
            )
        )
        lenerlabel.set_use_markup(True)

        boeklabel = Gtk.Label('<big><b>"{}"</b></big>  -  <big>{}</big>'.format(
                uitlening['titel'],
                uitlening['auteur'],
            )
        )
        boeklabel.set_use_markup(True)

        # Layout
        #
        grid = Gtk.Grid(
                row_spacing=8,
                column_spacing=8,
                margin=8,
                orientation=Gtk.Orientation.VERTICAL,
            )
        grid.add(lenerlabel)
        grid.add(boeklabel)
        self.get_content_area().add(grid)
        #self.set_default_size(200, 150)
        self.show_all()
