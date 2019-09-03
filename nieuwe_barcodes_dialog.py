import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

class NewBarcodesDialog(Gtk.Dialog):
    def __init__(self, parent, aantal):
        Gtk.Dialog.__init__(self, "Nieuw streepjescodes genereren", parent, 0,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
            )
        box = self.get_content_area()
        self.label = Gtk.Label("Aantal te genereren streepjescodes:", halign=Gtk.Align.START)
        self.aantal = Gtk.Entry()
        self.aantal.set_alignment(xalign=1)
        self.aantal.set_text(str(aantal))

        box.add(Gtk.Label())
        box.add(self.label)
        #box.add(Gtk.Label())
        box.add(self.aantal)
        box.add(Gtk.Label())

        self.show_all()

