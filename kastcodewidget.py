import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from kastcodelijst import KastcodeLijst
from kastcodedialog import KastcodeDialog

class KastcodeWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(
                margin=8,
                column_spacing=8,
                row_spacing=8,
                orientation=Gtk.Orientation.VERTICAL
            )
        self.parent = parent
        self.db = database
        self.invalidated = False

        self.lijst = KastcodeLijst()
        self.lijst.view.connect("row-activated", self.on_row_activated)

        nieuw_button = Gtk.Button("Nieuw", hexpand=False)
        nieuw_button.connect("clicked", self.on_nieuw_kastcode)
        wijzig_button = Gtk.Button("Wijzig", hexpand=False)
        wijzig_button.connect("clicked", self.on_wijzig_kastcode)
        verwijder_button = Gtk.Button("Verwijder", hexpand=False)
        verwijder_button.connect("clicked", self.on_verwijder_kastcode)

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
        kastcodes = self.db.alle_kastcodes() 
        self.lijst.load(kastcodes)

    def on_nieuw_kastcode(self, button):
        dialog = KastcodeDialog(self.parent, self.db)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            self.db.nieuwe_kastcode(**data)
        dialog.destroy()
        self.refresh()

    def on_row_activated(self, view, path, column):
        record = self.lijst.model[path]
        code_id = record[0]
        self.wijzig_kastcode(code_id)

    def on_wijzig_kastcode(self, button):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        code_id = record[0]
        self.wijzig_kastcode(code_id)

    def on_verwijder_kastcode(self, button):
        model, path = self.lijst.view.get_selection().get_selected_rows()
        if not path:
            return
        record = self.lijst.model[path]
        kastcode_id = record[0]
        usage_count = self.db.kastcode_usage(kastcode_id)
        if usage_count > 0:
            message = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Nog {} boeken hebben deze kastcode".format(usage_count)
            )
            message.format_secondary_text("Kastcode kan daarom niet verwijderd worden.")
            response = message.run()
        else:
            self.db.verwijder_kastcode(kastcode_id)
            self.refresh()
        message.destroy()

    def wijzig_kastcode(self, code_id):
        dialog = KastcodeDialog(self.parent, self.db, code_id)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen:
                self.db.update_table("kastcode", code_id, **wijzigingen)
                self.refresh()
        dialog.destroy()
