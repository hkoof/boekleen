import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from datalijst import DataLijst, ColumnDef
from terugbrengdialog import TerugbrengDialog

class LenersLijst(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(
                margin=12,
                column_spacing=12,
                row_spacing=12,
                column_homogeneous=True,
            )
        self.parent = parent
        self.db = database
        self.update_uitleningen = True

        columns = (
                ColumnDef("Persoon ID", "id", datatype=int),
                ColumnDef("Voornaam", "voornaam"),
                ColumnDef("Achternaam", "achternaam"),
            )
        self.lijst = DataLijst(columns, show_primary_key=False, expand=True)
        self.model = self.lijst.model
        if hasattr(self.parent, 'on_row_activated'):
            self.lijst.view.connect("row-activated", self.parent.on_row_activated)
        self.lijst.view.connect("cursor-changed", self.on_select)
        self.lijst.view.connect("focus-out-event", self.on_focus_out)

        self.leenmodel = Gtk.ListStore(str, str)
        self.leenview = Gtk.TreeView(
                enable_grid_lines=False,
        #        headers_visible=False,
                fixed_height_mode=False,
                margin=12,
            )
        self.leenview.set_can_focus(False)
        self.leenview.set_model(self.leenmodel)
        scroller = Gtk.ScrolledWindow()
        scroller.add(self.leenview)
        self.leenview.connect("row-activated", self.on_row_activate_leenview)

        renderer1 = Gtk.CellRendererText()
        col0 = Gtk.TreeViewColumn("isbn", renderer1, text=0)
        col0.set_visible(False)
        col1 = Gtk.TreeViewColumn("Boeken in leen", renderer1, text=1)
        col1.set_resizable(False)
        #col1.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col1.set_max_width(300)
        self.leenview.append_column(col0)
        self.leenview.append_column(col1)

        detail_frame = Gtk.Frame(margin=12)
        detail_frame.add(scroller)

        self.attach(self.lijst, 0, 0, 1, 1)
        self.attach(detail_frame, 1, 0, 1, 1)

    def load(self, personen):
        self.update_uitleningen = False
        self.lijst.load(personen)
        self.leenmodel.clear()
        self.update_uitleningen = True

    def get_selected(self):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return None
        record = self.lijst.model[path]
        persoon_id = record[0]
        return persoon_id

    def on_select(self, treeview):
        self.reload_leenview()

    def reload_leenview(self):
        if not self.update_uitleningen:
            return
        persoon_id = self.get_selected()
        if persoon_id == None:
            self.leenmodel.clear()
        uitleningen = self.db.uitleningen(persoon_id, uitgeleend=True)
        self.leenmodel.clear()
        for lening in uitleningen:
            row = ((lening['isbn'], '"{}"  -  {}'.format(lening['titel'], lening['auteur']),))
            self.leenmodel.append(row)

    def on_focus_out(self, treeview, event):
        self.reload_leenview()

    def on_row_activate_leenview(self, view, path, column):
        record = self.leenmodel[path]
        isbn = record[0]

        uitlening = self.db.uitgeleend(isbn)
        if uitlening:
            dialog = TerugbrengDialog(self.parent.parent, uitlening)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.db.brengterug(isbn)
                self.reload_leenview()
            dialog.destroy()
        else:
            print("error: {} {} is niet uitgeleend")
