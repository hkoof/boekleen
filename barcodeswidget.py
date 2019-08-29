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
        self.selection = self.lijst.view.get_selection()
        self.selection.connect("changed", self.on_select_row)
        self.lijst.view.connect("row-activated", self.on_row_activated)
        #self.lijst.view.connect("cursor-changed", self.on_select_row)

    
        nieuw_button = Gtk.Button("Genereer nieuwe barcodes")
        nieuw_button.connect("clicked", self.on_nieuw)
        self.verwijder_button = Gtk.Button("Verwijder")
        self.verwijder_button.connect("clicked", self.on_verwijder)
        print_button = Gtk.Button("Print")
        print_button.connect("clicked", self.on_print)

        self.bestaand_check = Gtk.CheckButton(label="Ook bestaande boeken")
        self.bestaand_check.connect("clicked", self.refresh)
        self.geprint_check = Gtk.CheckButton(label="Ook geprinte barcodes")
        self.geprint_check.connect("clicked", self.refresh)

        # layout
        #
        knoppen = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        knoppen.attach(nieuw_button, 1, 0, 1, 1)
        knoppen.attach(self.verwijder_button, 1, 1, 1, 1)
        knoppen.attach(print_button, 1, 2, 1, 1)

        selectie = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        selectie.attach(self.bestaand_check, 1, 0, 1, 1)
        selectie.attach(self.geprint_check, 1, 1, 1, 1)

        markeren = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )

        markeren_paneel = Gtk.Frame(label="Markeren")
        selectie_paneel = Gtk.Frame(label="Selecteren")
        actie_paneel = Gtk.Frame(label="Acties")

        markeren_paneel.add(markeren)
        selectie_paneel.add(selectie)
        actie_paneel.add(knoppen)

        paneel = Gtk.Grid(
                margin=16,
                column_spacing=16,
                row_spacing=16,
                orientation=Gtk.Orientation.HORIZONTAL,
                hexpand=True,
                #halign=Gtk.Align.END,
            )
        paneel.attach(selectie_paneel, 0, 0, 1, 1)
        paneel.attach(markeren_paneel, 1, 0, 1, 1)
        paneel.attach(Gtk.Label(hexpand=True), 2, 0, 1, 1)
        paneel.attach(actie_paneel, 3, 0, 1, 1)

        self.add(paneel)
        self.add(self.lijst)
        self.refresh()

    def refresh(self, dummy=None):
        bestaand = None if self.bestaand_check.get_active() else False
        printed = None if self.geprint_check.get_active() else False
        self.barcodes = self.db.get_barcodes(
                with_book=bestaand,
                printed=printed,
            )
        self.lijst.load(self.barcodes)

    def get_selected_rows(self):
        model, path = self.selection.get_selected_rows()
        if not path:
            return []
        result = list()
        for row in path:
            result.append(tuple([col for col in model[row]]))
        return result

    def disable_delete_button_if_custom_code_in_selection(self):
        enabled = True
        for row in self.get_selected_rows():
            print(row)
            if not row[2]:
                enabled = False
                break
        print(enabled)
        self.verwijder_button.set_sensitive(enabled)

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
        pass

    def on_select_row(self, view):
        self.disable_delete_button_if_custom_code_in_selection()

    def on_row_activated(self, view, path, column):
        #record = self.lijst.model[path]
        max_idx = max(len(self.barcodes) - 1, 0)
        begin_idx = path.get_indices()[0]
        end_idx = min(begin_idx + self.labels_per_page - 1, max_idx)

        endpath = Gtk.TreePath(end_idx)
        self.selection.select_range(path, endpath)
        self.disable_delete_button_if_custom_code_in_selection()

    def print_categorie(self, cat_id):
        dialog = CategorieDialog(self.parent, self.db, cat_id)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen:
                self.db.update_table("categorie", cat_id, **wijzigingen)
                self.refresh()
        dialog.destroy()
