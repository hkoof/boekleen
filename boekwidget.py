import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from datetime import datetime

from datalijst import DataLijst, ColumnDef
from boekdialog import BoekDialog
from recorddialog import ChoiceInput, ColoredChoiceInput
from uitleendialog import UitleenDialog
from terugbrengdialog import TerugbrengDialog

class BoekWidget(Gtk.Grid):
    def __init__(self, parent, database):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.invalidated = True

        columns = (
                ColumnDef("ISBN", "isbn"),
                ColumnDef("Titel", "titel"),
                ColumnDef("Auteur", "auteur"),
                ColumnDef("# Leningen", "leningen", datatype=int),
            )
        self.boeklijst = DataLijst(columns, show_primary_key=False, expand=True)
        self.boeklijst.view.connect("row-activated", self.on_row_activated)
        self.selection = self.boeklijst.view.get_selection()
        self.selection.connect("changed", self.on_select_row)

        # Selectie controls
        #
        self.categorie_select = ChoiceInput("Categorie", 1)
        categorien = [(str(cat['id']), cat['categorienaam']) for cat in self.db.alle_categorien()]
        categorien.insert(0, ('', '----[ Categorie ]----'))
        self.categorie_select.set_choices(categorien)
        self.categorie_select.widget.set_active_id('')
        self.categorie_select.widget.connect("changed", self.refresh)

        self.kastcode_select = ColoredChoiceInput("Kastcode", 1)
        kastcodes = self.db.alle_kastcodes()
        kastcodes.insert(0, {
            'id': '',
            'code': '----[ Kastcode ]----',
            'tekstkleur': 'black',
            'achtergrondkleur': 'rgba(1.0, 1.0, 1.0, .0)',
        })
        self.kastcode_select.set_choices(kastcodes)
        self.kastcode_select.widget.set_active_id('')
        self.kastcode_select.widget.connect("changed", self.refresh)

        self.status_select_alle = Gtk.RadioButton.new_with_label_from_widget(None, "Alle")
        self.status_select_alle.connect("toggled", self.on_status_select_toggled)

        self.status_select_aanwezig = Gtk.RadioButton.new_with_label_from_widget(self.status_select_alle, "Aanwezig")
        self.status_select_aanwezig.connect("toggled", self.on_status_select_toggled)

        self.status_select_uitgeleend = Gtk.RadioButton.new_with_label_from_widget(self.status_select_alle, "Uitgeleend")
        self.status_select_uitgeleend.connect("toggled", self.on_status_select_toggled)

        selectie_reset_button = Gtk.Button("Reset")
        selectie_reset_button.connect("clicked", self.on_selectie_reset_clicked)

        nieuw_boek_button = Gtk.Button("Nieuw")
        nieuw_boek_button.connect("clicked", self.on_nieuw_boek)
        self.wijzig_boek_button = Gtk.Button("Wijzig")
        self.wijzig_boek_button.connect("clicked", self.on_wijzig_boek)
        self.uitleenstatus_button = Gtk.Button("Uitleenstatus")
        self.uitleenstatus_button.connect("clicked", self.on_uitleenstatus_boek)
        self.verwijder_boek_button = Gtk.Button("Verwijder")
        self.verwijder_boek_button.connect("clicked", self.on_verwijder_boek)

        self.default_categorie = None
        self.default_kastcode = None

        # Zoek controls
        #
        self.zoek_input  = Gtk.Entry()
        self.zoek_input.connect("activate", self.on_zoek_input_activate)

        self.zoek_button = Gtk.Button("Zoek")
        self.zoek_leeg_button = Gtk.Button("Leeg")
        self.zoek_reset_button = Gtk.Button("Reset")

        self.zoek_button.connect("clicked", self.refresh)
        self.zoek_leeg_button.connect("clicked", self.on_zoek_leeg_clicked)
        self.zoek_reset_button.connect("clicked", self.on_zoek_reset_clicked)

        zoekvelden_paneel = Gtk.Frame(label="Zoekvelden")
        zoekvelden_grid = Gtk.Grid(margin=4, column_spacing=4, row_spacing=4, orientation=Gtk.Orientation.VERTICAL)
        self.zoekvelden = dict()
        for zoekveld in ('titel', 'auteur', 'omschrijving', 'trefwoorden'):
            veld = Gtk.CheckButton(label=zoekveld.capitalize())
            if zoekveld == 'titel':
                veld.set_active(True)
            veld.connect("toggled", self.refresh)
            zoekvelden_grid.add(veld)
            self.zoekvelden[zoekveld] = veld
        zoekvelden_paneel.add(zoekvelden_grid)

        # layout
        #
        zoekbutton_grid = Gtk.Grid(column_spacing=8, row_spacing=12, column_homogeneous=True)
        zoekbutton_grid.attach(self.zoek_reset_button, 0, 0, 1, 1)
        zoekbutton_grid.attach(self.zoek_leeg_button, 1, 0, 1, 1)
        zoekbutton_grid.attach(self.zoek_button, 2, 0, 2, 1)

        zoek_paneel = Gtk.Frame(label="Zoeken")
        selectie_paneel = Gtk.Frame(label="Selecteren")
        actie_paneel = Gtk.Frame(label="Acties")

        zoek_grid = Gtk.Grid(margin=12, column_spacing=8, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)
        selectie_grid = Gtk.Grid(margin=12, column_spacing=12, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)
        actie_grid = Gtk.Grid(margin=12, column_spacing=12, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)
        
        zoek_paneel.add(zoek_grid)
        selectie_paneel.add(selectie_grid)
        actie_paneel.add(actie_grid)
        
        zoek_grid.add(self.zoek_input)
        zoek_grid.add(zoekbutton_grid)
        zoek_grid.add(zoekvelden_paneel)

        status_select_grid = Gtk.Grid(
                margin=8,
                column_spacing=4,
                row_spacing=4,
                orientation=Gtk.Orientation.VERTICAL
            )

        status_select_grid.add(self.status_select_alle)
        status_select_grid.add(self.status_select_aanwezig)
        status_select_grid.add(self.status_select_uitgeleend)

        status_select_paneel = Gtk.Frame(label="Status")
        status_select_paneel.add(status_select_grid)

        selectie_grid.add(self.kastcode_select.widget)
        selectie_grid.add(self.categorie_select.widget)
        selectie_grid.add(status_select_paneel)
        #selectie_grid.add(Gtk.Label())
        selectie_grid.add(selectie_reset_button)

        actie_grid.add(nieuw_boek_button)
        actie_grid.add(self.wijzig_boek_button)
        actie_grid.add(self.uitleenstatus_button)
        actie_grid.add(self.verwijder_boek_button)

        paneel = Gtk.Grid(margin=16, column_spacing=16, row_spacing=16,
                orientation=Gtk.Orientation.HORIZONTAL,
                hexpand=True,
            )
        paneel.attach(zoek_paneel, 0, 0, 1, 1)
        paneel.attach(selectie_paneel, 1, 0, 1, 1)
        paneel.attach(Gtk.Label(hexpand=True), 2, 0, 1, 1)
        paneel.attach(actie_paneel, 3, 0, 1, 1)

        self.add(paneel)
        self.add(self.boeklijst)

    def refresh(self, dummy=None):
        selectie = dict()
        zoekvelden = dict()

        kastcode = self.kastcode_select.get_data()
        if kastcode:
            selectie['kastcode_id'] = kastcode

        categorie = self.categorie_select.get_data()
        if categorie:
            selectie['categorie_id'] = categorie

        zoekvelden = [naam for naam, veld in self.zoekvelden.items() if veld.get_active()]
        zoekstring = self.zoek_input.get_text()

        select_uitgeleend = None
        if self.status_select_aanwezig.get_active():
            select_uitgeleend = False
        elif self.status_select_uitgeleend.get_active():
            select_uitgeleend = True

        boeken = self.db.zoek_boeken(zoekstring, zoekvelden, selectie, select_uitgeleend)
        self.laad_boeken(boeken)
        self.invalidated = False

    def get_selected_isbn(self):
        model, path = self.selection.get_selected_rows()
        if not path:
            return
        record = self.boeklijst.model[path]
        isbn = record[0]
        return isbn

    def laad_boeken(self, boeken):
        self.boeklijst.load(boeken)
        self.wijzig_boek_button.set_sensitive(False)
        self.uitleenstatus_button.set_sensitive(False)
        self.verwijder_boek_button .set_sensitive(False)

    def on_zoek_input_activate(self, entry):
        self.parent.set_focus(None)
        self.refresh()

    def on_zoek_leeg_clicked(self, button):
        self.zoek_input.set_text('')
        self.refresh()

    def on_zoek_reset_clicked(self, button):
        self.zoek_input.set_text('')
        for naam, veld in self.zoekvelden.items():
            veld.set_active(naam == 'titel')
        self.refresh()

    def on_selectie_reset_clicked(self, button):
        self.categorie_select.widget.set_active(False)
        self.kastcode_select.widget.set_active(False)
        self.status_select_alle.set_active(True)

    def on_nieuw_boek(self, button):
        self.nieuw_boek()

    def nieuw_boek(self, isbn=None):
        dialog = BoekDialog(self.parent, self.db)
        dialog.set_default_choice("categorie_id", self.default_categorie)
        dialog.set_default_choice("kastcode_id", self.default_kastcode)
        if isbn:
            dialog.set_isbn(isbn)

        response = dialog.run()
        self.default_categorie = dialog.get_choice("categorie_id")
        self.default_kastcode = dialog.get_choice("kastcode_id")

        if response == Gtk.ResponseType.OK:
            data = dialog.get_data(False)
            if self.boek_geldig(data):
                self.db.nieuw_boek(
                        data.get("isbn"),
                        data.get("titel"),
                        data.get("auteur"),
                        data.get("categorie_id"),
                        data.get("kastcode_id"),
                        data.get("omschrijving"),
                        data.get("trefwoorden"),
                    )
        dialog.destroy()
        self.parent.invalidate()
        self.refresh()

    def on_status_select_toggled(self, button):
        if button.get_active():
            self.refresh()

    def on_uitleenstatus_boek(self, button):
        isbn = self.get_selected_isbn()
        uitlening = self.db.uitgeleend(isbn)
        if uitlening:
            dialog = TerugbrengDialog(self.parent, uitlening)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.db.brengterug(isbn)
                self.refresh()
            dialog.destroy()
        else:
            boek = self.db.boeken(isbn)
            dialog = UitleenDialog(self.parent, self.db, boek)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                lener = dialog.get_lener()
                #lener = self.db.persoon(lener)
                if not lener:
                    print("error: onbekende lener: {}".format(self.lener))
                else:
                    self.db.leenuit(lener, isbn)
            dialog.destroy()

    def on_wijzig_boek(self, button):
        isbn = self.get_selected_isbn()
        self.wijzig_boek(isbn)

    def on_verwijder_boek(self, button):
        isbn = self.get_selected_isbn()
        self.verwijder_boek(isbn)

    def on_row_activated(self, view, path, column):
        record = self.boeklijst.model[path]
        isbn = record[0]
        self.wijzig_boek(isbn)

    def verwijder_boek(self, isbn):
        zekerweten = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "U staat op het punt een boek te verwijderen"
            )
        zekerweten.format_secondary_text("Weet u 't wel zeker?")
        response = zekerweten.run()
        if response == Gtk.ResponseType.YES:
            self.db.verwijder_boek(isbn)
            self.parent.invalidate()
            self.refresh()
        zekerweten.destroy()

    def boek_geldig(self, editted):
        titel = editted.get('titel')
        auteur = editted.get('auteur')
        valid = True
        if titel is not None:
            if len(titel) < 3:
                valid = False
        if auteur is not None:
            if len(auteur) < 3:
                valid = False
        if not valid:
            message = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "Titel en auteur moeten tenminste 3 tekens lang zijn"
            )
            message.format_secondary_text("Wijzigingen daarom niet opgeslagen")
            response = message.run()
            message.destroy()
        return valid

    def wijzig_boek(self, isbn):
        dialog = BoekDialog(self.parent, self.db, isbn)
        barcode_rec = self.db.get_barcode_record(isbn)
        is_printbaar = False
        if barcode_rec and not barcode_rec['printtime']:
            is_printbaar = True
        dialog.printbaar.set_active(is_printbaar)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen and self.boek_geldig(wijzigingen):
                self.db.update_table("boeken", ("isbn", isbn), **wijzigingen)
                self.parent.invalidate()

            if is_printbaar != dialog.printbaar.get_active():
                if dialog.printbaar.get_active():
                    self.db.set_barcode_record(isbn, dialog.items['titel'].widget.get_text())
                else:
                    self.db.delete_barcode_record(isbn)
        dialog.destroy()

    def on_select_row(self, view):
        self.wijzig_boek_button.set_sensitive(True)
        self.uitleenstatus_button.set_sensitive(True)
        self.verwijder_boek_button .set_sensitive(True)

    def on_isbn_scan(self, isbn):
        boek = self.db.zoek_boeken(isbn, ('isbn',))
        if boek:
            boek = boek[0]
            verwijderd = boek['verwijdertijdstip']
            if verwijderd:
                tijdstip = datetime.fromtimestamp(verwijderd)
                dialog = Gtk.MessageDialog(
                        self.parent,
                        0,
                        Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO,
                        "Boek is verwijderd op {}".format(
                            tijdstip.strftime('%A %w %B %Y om %X')
                        )
                    )
                dialog.format_secondary_text("Terughalen uit de prullebak?")
                response = dialog.run()
                dialog.destroy()
                if response == Gtk.ResponseType.YES:
                    self.db.update_table("boeken", ("isbn", isbn), verwijdertijdstip=None)
                else:
                    return

            self.zoek_input.set_text(isbn)
            self.laad_boeken((boek,))
            self.boeklijst.view.set_cursor(Gtk.TreePath(0))
            self.boeklijst.view.grab_focus()
            self.wijzig_boek(isbn)
        else:
            self.nieuw_boek(isbn)
