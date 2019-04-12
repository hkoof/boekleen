from collections import OrderedDict

from recorddialog import RecordDialog, TextInput

class CategorieDialog(RecordDialog):
    def __init__(self, parent, database, cat_id=None):
        self.db = database

        self.items = OrderedDict()
        self.items["categorienaam"] = TextInput("Categorie", 1)

        self.categorie = self.db.categorie(cat_id)
        super().__init__(parent, "Categorie")
        self.populate(self.categorie)

