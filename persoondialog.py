from collections import OrderedDict

from recorddialog import RecordDialog, TextInput, TextCompletionInput

class PersoonDialog(RecordDialog):
    def __init__(self, parent, database, persoon_id=None):
        self.db = database

        self.items = OrderedDict()
        self.items["voornaam"] = TextInput("Voornaam", 1)
        self.items["achternaam"] = TextInput("Achternaam", 2)
        self.items["klas"] = TextCompletionInput("Klas", 1)
        self.items["klas"].set_completion_data(self.db.alle_klassen())

        self.persoon = self.db.persoon(persoon_id)
        if self.persoon:
            dialog_titel = self.persoon['voornaam'] + " " + self.persoon['achternaam']
        else:
            dialog_titel = "Nieuwe lener"

        super().__init__(parent, dialog_titel)
        self.populate(self.persoon)

    def set_isbn(self, isbn):
        self.items['isbn'].widget.set_text(isbn)
        self.items["isbn"].set_editable(False)
        self.items["titel"].widget.grab_focus()
