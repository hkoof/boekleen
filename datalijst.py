import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

class ColumnDef():
    def __init__(self, titel, dbnaam, breedte=None, sorteerbaar=True, datatype=str):
        self.titel = titel
        self.dbnaam = dbnaam
        self.breedte = breedte
        self.sorteerbaar = sorteerbaar
        self.datatype = datatype

class DataLijst(Gtk.ScrolledWindow):
    def __init__(self, columns, *args, show_primary_key=True, **kwargs):
        #
        # columns is sequence van ColumnDef instanties
        #
        # De eerste (columns[0]) moet de primary key zijn waar de db-record
        # uniek mee kan worden geindentificeerd.
        #
        super().__init__(*args, **kwargs)
        self.view = Gtk.TreeView()
        self.view.set_enable_search(False)
        self.view.set_grid_lines(2)

        self.columns = columns
        typelist = list()
        for col in self.columns:
            typelist.append(col.datatype)
        self.model = Gtk.ListStore(*typelist)
        self.view.set_model(self.model)

        for i, coldef in enumerate(self.columns):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(coldef.titel, renderer, text=i)
            if i == 0 and not show_primary_key:
                col.set_visible(False)
            else:
                if coldef.sorteerbaar:
                    col.set_sort_column_id(i)
                col.set_spacing(100)
                col.set_resizable(True)
                col.set_expand(True)
            self.view.append_column(col)

        self.add(self.view)

    def load(self, data):
        self.model.clear()
        for rec in data:
            row = [rec[coldef.dbnaam] for coldef in self.columns]
            self.model.append(row)

