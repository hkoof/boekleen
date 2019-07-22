import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

from datalijst import DataLijst, ColumnDef
from categoriedialog import CategorieDialog

class BarcodesWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.invalidated = False
        self.labels_per_page = 6

        columns = (
                ColumnDef("Code", "isbn", datatype=str),
                ColumnDef("Geprint", "printtime"),
                ColumnDef("Opmerking", "notes"),
            )
        self.lijst = DataLijst(columns, show_primary_key=True, expand=True, multiselect=True)
        self.lijst.view.connect("row-activated", self.on_row_activated)

        nieuw_button = Gtk.Button("Genereer nieuwe barcodes")
        nieuw_button.connect("clicked", self.on_nieuw)
        verwijder_button = Gtk.Button("Verwijder")
        verwijder_button.connect("clicked", self.on_verwijder)
        print_button = Gtk.Button("Print")
        print_button.connect("clicked", self.on_print)

        self.bestaand_check = Gtk.CheckButton(label="Alleen bestaande boeken")
        self.bestaand_check.connect("clicked", self.refresh)
        self.geprint_check = Gtk.CheckButton(label="Alleen geprinte barcodes")
        self.geprint_check.connect("clicked", self.refresh)

        # layout
        #
        knoppen = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        knoppen.attach(nieuw_button, 1, 0, 1, 1)
        knoppen.attach(verwijder_button, 1, 1, 1, 1)
        knoppen.attach(print_button, 1, 2, 1, 1)

        selectie = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        selectie.attach(self.bestaand_check, 1, 0, 1, 1)
        selectie.attach(self.geprint_check, 1, 1, 1, 1)

        paneel = Gtk.Grid(
                margin=8,
                column_spacing=8,
                row_spacing=8,
                halign=Gtk.Align.END,
            )
        #paneel.attach(Gtk.Label(), 0, 0, 1, 1)
        paneel.attach(selectie, 0, 0, 1, 1)
        paneel.attach(knoppen, 1, 0, 1, 1)

        self.add(paneel)
        self.add(self.lijst)
        self.refresh()

    def refresh(self, dummy=None):
        bestaand = self.bestaand_check.get_active()
        printed = self.geprint_check.get_active()
        if not bestaand and not printed:
            self.barcodes = self.db.get_barcodes()
        else:
            self.barcodes = self.db.get_barcodes(
                    with_book=bestaand,
                    printed=printed,
                )
        self.lijst.load(self.barcodes)

    def on_verwijder(self, button):
        print("verwijderen barcode niet geimplemtneerd nog")

    def on_nieuw(self, button):
        dialog = CategorieDialog(self.parent, self.db)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data(False)
            self.db.nieuwe_categorie(
                    data.get("categorienaam"),
                )
        dialog.destroy()
        self.refresh()

    def on_print(self, button):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        cat_id = record[0]
        self.print_categorie(cat_id)

    def on_row_activated(self, view, path, column):
        #record = self.lijst.model[path]
        max_idx = max(len(self.barcodes) - 1, 0)
        begin_idx = path.get_indices()[0]
        end_idx = min(begin_idx + self.labels_per_page - 1, max_idx)

        selection = self.lijst.view.get_selection()
        endpath = Gtk.TreePath(end_idx)
        selection.select_range(path, endpath)

    def print_categorie(self, cat_id):
        dialog = CategorieDialog(self.parent, self.db, cat_id)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen:
                self.db.update_table("categorie", cat_id, **wijzigingen)
                self.refresh()
        dialog.destroy()
