import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from kastcodedialog import KastcodeDialog

class KastcodeLijst(Gtk.ScrolledWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, expand=True, **kwargs)
        self.model = Gtk.ListStore(int, str, Gdk.RGBA, Gdk.RGBA)

        self.view = Gtk.TreeView()
        self.view.set_grid_lines(2)
        self.view.set_model(self.model)
        self.add(self.view)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(
                "Kastcode",
                renderer,
                text=1,
            )
        self.view.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(
                "Gekleurd",
                renderer,
                text=1,
                foreground_rgba=2,
                background_rgba=3,
            )
        self.view.append_column(column)

    def load(self, data):
        self.model.clear()
        for rec in data:
            fg_rgba = Gdk.RGBA() ; fg_rgba.parse(rec['tekstkleur'])
            bg_rgba = Gdk.RGBA() ; bg_rgba.parse(rec['achtergrondkleur'])
            row = (rec['id'], rec['code'], fg_rgba, bg_rgba)
            self.model.append(row)
