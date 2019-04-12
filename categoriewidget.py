import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

from datalijst import DataLijst, ColumnDef
from categoriedialog import CategorieDialog

class CategorieWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.invalidated = False

        columns = (
                ColumnDef("Categorie ID", "id", datatype=int),
                ColumnDef("Categorie", "categorienaam"),
            )
        self.lijst = DataLijst(columns, show_primary_key=False, expand=True)
        self.lijst.view.connect("row-activated", self.on_row_activated)

        nieuw_button = Gtk.Button("Nieuw")
        nieuw_button.connect("clicked", self.on_nieuw)
        wijzig_button = Gtk.Button("Wijzig")
        wijzig_button.connect("clicked", self.on_wijzig)
        verwijder_button = Gtk.Button("Verwijder")
        verwijder_button.connect("clicked", self.on_verwijder)

        # layout
        #
        paneel = Gtk.Grid(
                margin=8,
                column_spacing=8,
                row_spacing=8,
                halign=Gtk.Align.END,
            )
        paneel.attach(Gtk.Label(), 0, 0, 1, 1)
        paneel.attach(nieuw_button, 1, 0, 1, 1)
        paneel.attach(wijzig_button, 1, 1, 1, 1)
        paneel.attach(verwijder_button, 1, 2, 1, 1)

        self.add(paneel)
        self.add(self.lijst)
        self.refresh()

    def refresh(self):
        categorien = self.db.alle_categorien() 
        self.lijst.load(categorien)

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

    def on_wijzig(self, button):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        cat_id = record[0]
        self.wijzig_categorie(cat_id)

    def on_verwijder(self, button):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        isbn = record[0]
        self.verwijder_categorie(isbn)

    def on_row_activated(self, view, path, column):
        record = self.lijst.model[path]
        isbn = record[0]
        self.wijzig_categorie(isbn)

    def verwijder_categorie(self, cat_id):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        categorie_id = record[0]
        usage_count = self.db.categorie_usage(categorie_id)
        if usage_count > 0:
            message = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Nog {} boeken hebben deze categorie".format(usage_count)
            )
            message.format_secondary_text("Categorie kan daarom niet verwijderd worden.")
            response = message.run()
        else:
            self.db.verwijder_categorie(categorie_id)
            self.refresh()
        message.destroy()

    def wijzig_categorie(self, cat_id):
        dialog = CategorieDialog(self.parent, self.db, cat_id)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen:
                self.db.update_table("categorie", cat_id, **wijzigingen)
                self.refresh()
        dialog.destroy()
