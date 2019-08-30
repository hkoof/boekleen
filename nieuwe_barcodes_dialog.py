import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

class NewBarcodesDialog(Gtk.Dialog):
    def __init__(self, parent, aantal):
        Gtk.Dialog.__init__(self, "Nieuw codes genereren", parent, 0,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
            )
        box = self.get_content_area()
        self.label = Gtk.Label("Aantal te genereren codes:", halign=Gtk.Align.END)
        self.aantal = Gtk.Entry()
        box.add(self.label)
        box.add(self.aantal)
        self.aantal.set_text(str(aantal))
        self.show_all()

