import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class RecordDialog(Gtk.Dialog):
    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self,
                title,
                parent,
                Gtk.DialogFlags.MODAL,
            )
        self.set_default_size(150, 100)
        self.set_default_response(Gtk.ResponseType.OK)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL).set_can_focus(False)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.box = self.get_content_area()
        grid = Gtk.Grid(margin=12, column_spacing=8, row_spacing=8, column_homogeneous=True)

        i = 0
        for naam, item in self.items.items():
            grid.attach(item.label, 0, i, 1 , 1)
            grid.attach(item.widget, 1, i, item.width, 1)
            i += 1

        self.box.add(grid)
        self.show_all()

    def populate(self, data):
        if not data:
            return
        for name, value in data.items():
            if name in self.items:
                self.items[name].set_data(value)

    def get_data(self, only_modified=True):
        data = dict()
        for naam, item in self.items.items():
            changed_data = item.get_data(only_modified)
            if changed_data is not None:
                data[naam] = changed_data
        return data

    def set_default_choice(self, name, value):
        if name and value:
            self.items[name].set_data(value)

    def get_choice(self, name):
        return self.items[name].get_data() if name else None


class DataInput: # Base class voor concrete Input widgets
    def __init__(self, label, width):
        self.label = Gtk.Label(label, halign=Gtk.Align.END)
        self.width = width
        self.modified = False
        self.original_data = None

    def set_editable(self, enable):
        self.widget.set_editable(enable)

class Text(DataInput):
    def __init__(self, label, width):
        super().__init__(label, width)
        self.widget = Gtk.Label("-----------", halign=Gtk.Align.START)

    def set_data(self, text):
        self.widget.set_label(text)

    def get_data(self, only_modified=True):
        return None

class TextInput(DataInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Gtk.Entry()

    def set_data(self, text):
        self.original_data = text
        self.widget.set_text(text if text else "")

    def get_data(self, only_modified=False):
        data = self.widget.get_text()
        if not only_modified or data != self.original_data:
            return data
        return None

class TextCompletionInput(TextInput):
    def __init__(self, *args, completion_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.completion_model = Gtk.ListStore(str)
        completion = Gtk.EntryCompletion()
        self.widget.set_completion(completion)
        completion.set_model(self.completion_model)
        completion.set_text_column(0)

        if completion_data:
            self.set_completion_data(completion_data)

    def set_completion_data(self, completion_data):
        for record in completion_data:
            self.completion_model.append((record,))

class ChoiceInput(DataInput):
    def __init__(self, *args, choices=None, select=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None
        self.original_data = None
        self.choices_model = Gtk.ListStore(str, str)
        if choices:
            self.set_choices(choices)
        if select:
            self.set_data(select)

        self.widget = Gtk.ComboBox.new_with_model(self.choices_model)
        renderer= Gtk.CellRendererText()
        self.widget.pack_start(renderer, True)
        self.widget.add_attribute(renderer, "text", 1)
        self.widget.connect("changed", self.on_changed)
        self.widget.set_id_column(0)

    def set_data(self, key):
        self.widget.set_active_id(str(key))
        self.data = key
        self.original_data = key

    def get_data(self, only_modified=False):
        if not only_modified or self.data != self.original_data:
            return self.data
        return None

    def set_choices(self, choices):
        for choice in choices:
            self.choices_model.append(choice)

    def on_changed(self, combo):
        idx = self.widget.get_active_iter()
        if idx != None:
            self.data = self.choices_model[idx][0]

class ColoredChoiceInput(ChoiceInput):
    def __init__(self, *args, choices=None, select=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices_model = Gtk.ListStore(str, str, Gdk.RGBA, Gdk.RGBA)
        if choices:
            self.set_choices(choices)
        if select:
            self.set_data(select)

        self.widget = Gtk.ComboBox.new_with_model(self.choices_model)
        renderer= Gtk.CellRendererText()
        self.widget.pack_start(renderer, True)
        self.widget.add_attribute(renderer, "text", 1)
        self.widget.add_attribute(renderer, "foreground_rgba", 2)
        self.widget.add_attribute(renderer, "background_rgba", 3)
        self.widget.connect("changed", self.on_changed)
        self.widget.set_id_column(0)

    def set_choices(self, choices):
        for rec in choices:
            fg_rgba = Gdk.RGBA() ; fg_rgba.parse(rec['tekstkleur'])
            bg_rgba = Gdk.RGBA() ; bg_rgba.parse(rec['achtergrondkleur'])
            choice = (str(rec['id']), rec['code'], fg_rgba, bg_rgba)

            self.choices_model.append(choice)

