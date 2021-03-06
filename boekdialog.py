import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from collections import OrderedDict

from recorddialog import RecordDialog, Text, TextInput, TextCompletionInput, ChoiceInput, ColoredChoiceInput

class BoekDialog(RecordDialog):
    def __init__(self, parent, database, isbn=None):
        self.db = database

        self.items = OrderedDict()
        self.items["isbn"] = TextInput("ISBN", 1)
        self.items["titel"] = TextInput("Titel", 2)

        self.items["uitgeleend"] = Text("Uitgeleend aan:", 2)

        self.items["auteur"] = TextCompletionInput("Auteur", 1)
        self.items["auteur"].set_completion_data(self.db.alle_auteurs())

        self.items["kastcode_id"] = ColoredChoiceInput("Kastcode", 1)
        self.items["kastcode_id"].set_choices(self.db.alle_kastcodes())

        self.items["categorie_id"] = ChoiceInput("Categorie", 1)
        categorien = [(str(cat['id']), cat['categorienaam']) for cat in self.db.alle_categorien()]
        self.items["categorie_id"].set_choices(categorien)

        self.items["omschrijving"] = TextInput("Omschrijving", 2)
        self.items["trefwoorden"] = TextInput("Trefwoorden", 2)

        self.boek = self.db.boek(isbn)
        if self.boek:
            dialog_titel = self.boek['titel']
            self.items["isbn"].set_editable(False)
        else:
            dialog_titel = "Nieuw boek"
        super().__init__(parent, dialog_titel)

        # Extra item voor printbaar maken van barcode
        #
        self.printbaar = Gtk.CheckButton("Streepjescode printbaar")
        self.grid.attach_next_to(self.printbaar, None, Gtk.PositionType.BOTTOM, 1, 1)
        #self.grid.attach(self.printbaar, 1, 13 , 1, 1)

        self.populate(self.boek)
        if isbn:
            self.set_isbn(isbn)

    def populate(self, data):
        super().populate(data)
        self.show_all()

    def set_isbn(self, isbn):
        self.items['isbn'].widget.set_text(isbn)
        self.items["isbn"].widget.set_can_focus(False)
        self.items["titel"].widget.grab_focus()
        uitlening = self.db.uitgeleend(isbn)
        if uitlening:
            lener = "{} {}".format(uitlening["voornaam"], uitlening["achternaam"])
            klas = uitlening["klas"]
            if klas:
                lener = "{} (klas: {})".format(lener, klas)
        else:
            lener ="-----------"
        self.items["uitgeleend"].set_data(lener)

