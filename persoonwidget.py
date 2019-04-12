import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import sys

from lenerslijst import LenersLijst
from persoondialog import PersoonDialog
from recorddialog import ChoiceInput

class PersoonWidget(Gtk.Grid):
    def __init__(self, parent, database, read_only=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.db = database
        self.read_only = read_only
        self.invalidated = False

        self.lijst = LenersLijst(self, database)

        # Selectie controls
        #
        self.klas_select = ChoiceInput("Klas", 1)
        klassen = list()
        i = 1
        for klas in self.db.alle_klassen():
            if not klas:
                continue
            klassen.append((str(i), klas))
            i += 1
        klassen.insert(0, ('', '----[ Klas ]----'))
        self.klas_select.set_choices(klassen)
        self.klas_select.widget.set_active_id('')
        self.klas_select.widget.connect("changed", self.refresh)

        # Actie controls
        #
        if not self.read_only:
            nieuw_button = Gtk.Button("Nieuw")
            nieuw_button.connect("clicked", self.on_nieuw)
            wijzig_button = Gtk.Button("Wijzig")
            wijzig_button.connect("clicked", self.on_wijzig)
            verwijder_button = Gtk.Button("Verwijder")
            verwijder_button.connect("clicked", self.on_verwijder)

            actie_grid = Gtk.Grid(margin=12, column_spacing=12, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)
            actie_grid.add(nieuw_button)
            actie_grid.add(wijzig_button)
            actie_grid.add(verwijder_button)

            actie_paneel = Gtk.Frame(label="Acties", halign=Gtk.Align.START)
            actie_paneel.add(actie_grid)

        
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
        for zoekveld in ('voornaam', 'achternaam'):
            veld = Gtk.CheckButton(label=zoekveld.capitalize())
            if zoekveld == 'voornaam':
                veld.set_active(True)
            veld.connect("toggled", self.refresh)
            zoekvelden_grid.add(veld)
            self.zoekvelden[zoekveld] = veld
        zoekvelden_paneel.add(zoekvelden_grid)

        # layout
        #
        zoekbutton_grid = Gtk.Grid(column_spacing=12, row_spacing=12, column_homogeneous=True)
        zoekbutton_grid.attach(self.zoek_reset_button, 0, 0, 1, 1)
        zoekbutton_grid.attach(self.zoek_leeg_button, 1, 0, 1, 1)
        zoekbutton_grid.attach(self.zoek_button, 2, 0, 2, 1)

        zoek_paneel = Gtk.Frame(label="Zoeken")
        selectie_paneel = Gtk.Frame(label="Selecteren", hexpand=True)

        zoek_grid = Gtk.Grid(margin=12, column_spacing=12, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)
        selectie_grid = Gtk.Grid(margin=12, column_spacing=12, row_spacing=12, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)

        zoek_paneel.add(zoek_grid)
        selectie_paneel.add(selectie_grid)

        zoek_grid.add(self.zoek_input)
        zoek_grid.add(zoekbutton_grid)
        zoek_grid.add(zoekvelden_paneel)

        selectie_grid.add(self.klas_select.widget)
        selectie_grid.add(Gtk.Label())

        paneel = Gtk.Grid(
                margin=16,
                column_spacing=16,
                row_spacing=16,
                hexpand=True,
            )
        paneel.attach(zoek_paneel, 0, 0, 1, 1)
        paneel.attach(selectie_paneel, 1, 0, 1, 1)
        if not self.read_only:
            paneel.attach(Gtk.Label(hexpand=True), 2, 0, 1, 1)
            paneel.attach(actie_paneel, 3, 0, 1, 1)

        self.add(paneel)
        self.add(self.lijst)
        self.refresh()

    def refresh(self, dummy=None):
        selectie = dict()
        zoekvelden = dict()

        it = self.klas_select.widget.get_active_iter()
        if it:
            model = self.klas_select.choices_model
            if model[it][0]:
                selectie['klas'] = model[it][1]

        zoekvelden = [naam for naam, veld in self.zoekvelden.items() if veld.get_active()]
        zoekstring = self.zoek_input.get_text()

        personen = self.db.zoek_personen(zoekstring, zoekvelden, selectie)
        self.lijst.load(personen)

    def on_zoek_input_activate(self, entry):
        self.parent.set_focus(None)
        self.refresh()

    def on_zoek_leeg_clicked(self, button):
        self.zoek_input.set_text('')
        self.refresh()

    def on_zoek_reset_clicked(self, button):
        self.zoek_input.set_text('')
        for naam, veld in self.zoekvelden.items():
            veld.set_active(naam == 'voornaam')
        self.refresh()

    def on_selectie_reset_clicked(self, button):
        self.klas_select.widget.set_active(0)

    def on_nieuw(self, button):
        if self.read_only:
            print("BUG: on_nieuw() called. Should not happen!", file=sys.stderr)
            return
        dialog = PersoonDialog(self.parent, self.db)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data(False)
            self.db.nieuw_persoon(
                    data.get("voornaam"),
                    data.get("achternaam"),
                    data.get("klas"),
                )
        dialog.destroy()
        self.parent.invalidate()
        self.refresh()

    def on_wijzig(self, button):
        if self.read_only:
            print("BUG: on_wijzig() called. Should not happen!", file=sys.stderr)
            return
        persoon_id = self.lijst.get_selected()
        self.wijzig_persoon(persoon_id)

    def on_verwijder(self, button):
        if self.read_only:
            print("BUG: on_verwijder() called. Should not happen!", file=sys.stderr)
            return
        persoon_id = self.lijst.get_selected()
        self.verwijder_persoon(persoon_id)

    def on_row_activated(self, view, path, column):
        if self.read_only:
            return
        record = self.lijst.model[path]
        persoon_id = record[0]
        self.wijzig_persoon(persoon_id)

    def verwijder_persoon(self, persoon_id):
        zekerweten = Gtk.MessageDialog(
                self.parent,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "U staat op het punt iemand uit het bestand te verwijderen"
            )
        zekerweten.format_secondary_text("Weet u 't wel zeker?")
        response = zekerweten.run()
        if response == Gtk.ResponseType.YES:
            self.db.verwijder_persoon(persoon_id)
            self.parent.invalidate()
            self.refresh()
        zekerweten.destroy()

    def wijzig_persoon(self, persoon_id):
        dialog = PersoonDialog(self.parent, self.db, persoon_id)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wijzigingen = dialog.get_data()
            if wijzigingen:
                self.db.update_table("personen", persoon_id, **wijzigingen)
                self.parent.invalidate()
                self.refresh()
        dialog.destroy()
