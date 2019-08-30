import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

from datalijst import DataLijst, ColumnDef
from barcodeprint import BarcodePrinter
from nieuwe_barcodes_dialog import NewBarcodesDialog

class BarcodesWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.invalidated = False

        self.printer = BarcodePrinter()

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
    
        self.nieuw_button = Gtk.Button("Genereer nieuwe barcodes")
        self.nieuw_button.connect("clicked", self.on_nieuw)
        self.verwijder_button = Gtk.Button("Verwijder")
        self.verwijder_button.connect("clicked", self.on_verwijder)
        self.print_button = Gtk.Button("Print")
        self.print_button.connect("clicked", self.on_print)

        self.bestaand_check = Gtk.CheckButton(label="Ook bestaande boeken")
        self.bestaand_check.connect("clicked", self.refresh)
        self.geprint_check = Gtk.CheckButton(label="Ook geprinte barcodes")
        self.geprint_check.connect("clicked", self.refresh)

        self.bulk_select_button = Gtk.Button(label="Selecteer pagina vol")
        self.bulk_select_button.connect("clicked", self.on_bulk_select)
        self.bulk_label = Gtk.Label("(dubbel-klikken op een regel kan ook)")

        # layout
        #
        knoppen_grid = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        knoppen_grid.attach(self.nieuw_button, 1, 0, 1, 1)
        knoppen_grid.attach(self.verwijder_button, 1, 1, 1, 1)
        knoppen_grid.attach(self.print_button, 1, 2, 1, 1)

        filter_grid = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        filter_grid.attach(self.bestaand_check, 1, 0, 1, 1)
        filter_grid.attach(self.geprint_check, 1, 1, 1, 1)

        selecteren_grid = Gtk.Grid(
                margin=12,
                column_spacing=8,
                row_spacing=8,
            )
        selecteren_grid.attach(self.bulk_select_button, 1, 0, 1, 1)
        selecteren_grid.attach(self.bulk_label, 1, 1, 1, 1)

        selecteren_paneel = Gtk.Frame(label="Selecteren")
        selectie_paneel = Gtk.Frame(label="Filteren")
        actie_paneel = Gtk.Frame(label="Acties")

        selecteren_paneel.add(selecteren_grid)
        selectie_paneel.add(filter_grid)
        actie_paneel.add(knoppen_grid)

        paneel = Gtk.Grid(
                margin=16,
                column_spacing=16,
                row_spacing=16,
                orientation=Gtk.Orientation.HORIZONTAL,
                hexpand=True,
            )
        paneel.attach(selectie_paneel, 0, 0, 1, 1)
        paneel.attach(selecteren_paneel, 1, 0, 1, 1)
        paneel.attach(Gtk.Label(hexpand=True), 2, 0, 1, 1)
        paneel.attach(actie_paneel, 3, 0, 1, 1)

        self.add(paneel)
        self.add(self.lijst)
        self.refresh()

    def refresh(self, dummy=None):
        self.invalidated = True
        bestaand = None if self.bestaand_check.get_active() else False
        printed = None if self.geprint_check.get_active() else False
        self.barcodes = self.db.get_barcodes(
                with_book=bestaand,
                printed=printed,
            )
        self.lijst.load(self.barcodes)
        self.disable_print_button_if_needed()
        self.disable_delete_button_if_needed()
        self.bulk_select_button.set_label("Selecteer hele pagina erbij\n({} codes)".format(self.get_labels_per_page()))

    def get_labels_per_page(self):
        self.printer.loadconfig()
        return self.printer.get_codes_per_page()

    def get_selected_rows(self):
        model, path = self.selection.get_selected_rows()
        if not path:
            return []
        result = list()
        index = 0
        for row in path:
            rec = [col for col in model[row]]
            rec.insert(0, index)
            index += 1
            result.append(rec)
        return result

    def disable_delete_button_if_needed(self):
        enabled = False
        for row in self.get_selected_rows():
            enabled = True
            if not row[3]:
                enabled = False
                break
        self.verwijder_button.set_sensitive(enabled)

    def disable_print_button_if_needed(self):
        self.print_button.set_sensitive(self.get_selected_rows())

    def on_verwijder(self, button):
        print("verwijderen barcode niet geimplemtneerd nog")

    def on_nieuw(self, button):
        aantal = None
        dialog = NewBarcodesDialog(self.parent, int(self.get_labels_per_page()))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            str_aantal = dialog.aantal.get_text()
            try:
                aantal = int(str_aantal)
            except ValueError:
                aantal = None
                errdialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.CANCEL, 'Error: "{}" is geen geldig aantal'.format(str_aantal))
                errdialog.run()
                errdialog.destroy()
            if aantal:
                self.db.create_new_barcodes(num=aantal)
                self.refresh()
        dialog.destroy()

    def on_print(self, button):
        codes = [row[1] for row in self.get_selected_rows()]
        self.printer.print(codes)
        for code in codes:
            self.db.mark_barcode_printed(code)
        self.refresh()

    def on_select_row(self, view):
        self.disable_delete_button_if_needed()
        self.disable_print_button_if_needed()

    def on_row_activated(self, view, path, column):
        self.auto_select_codes(path.get_indices()[0])

    def on_bulk_select(self, button):
        self.auto_select_codes()

    def auto_select_codes(self, start=0, num=None):
        if num == None:
            num = self.get_labels_per_page()

        startpath = Gtk.TreePath(start)

        max_idx = max(len(self.barcodes) - 1, 0)
        end_idx = min(start + num - 1, max_idx)
        endpath = Gtk.TreePath(end_idx)

        self.selection.select_range(startpath, endpath)
        self.disable_delete_button_if_needed()
