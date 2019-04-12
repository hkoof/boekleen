import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

sample_css = """label {{
    color: {fg};
    background-color: {bg};
    font-weight: bold;
}}
"""

def rgba2hex(rgba):
    r = int(rgba.red * 255)
    g = int(rgba.green * 255)
    b = int(rgba.blue * 255)
    hex_kleur = "#{:02X}{:02X}{:02X}".format(r,g,b)
    return hex_kleur

class KastcodeDialog(Gtk.Dialog):
    def __init__(self, parent, database, code_id=None):
        super().__init__(
                "Kastcode",
                parent,
                Gtk.DialogFlags.MODAL,
            )
        self.set_default_size(150, 100)
        self.set_default_response(Gtk.ResponseType.OK)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL).set_can_focus(False)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.db = database

        grid = Gtk.Grid(
                row_spacing=8,
                column_spacing=8,
                margin=8,
            )

        self.code_input = Gtk.Entry()
        self.kleur_letters = Gtk.ColorButton()
        self.kleur_achtergrond = Gtk.ColorButton()
        self.kleurlabel = Gtk.Label("", expand=False)

        self.code_input.connect('changed', self.on_text_changed)
        self.kleur_letters.connect('color_set', self.on_color_set)
        self.kleur_achtergrond.connect('color_set', self.on_color_set)
        self.code_input.set_text("Sample")

        self._css = Gtk.CssProvider()
        self.kleurlabel.get_style_context().add_provider(
                self._css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

        voorbeeld_frame = Gtk.Frame(label="Voorbeeld")
        voorbeeld_frame.set_size_request(150, 150)
        voorbeeld_grid = Gtk.Grid(
                row_spacing=8,
                column_spacing=8,
                row_homogeneous=True,
                #column_homogeneous=True,
            )
        voorbeeld_grid.attach(Gtk.Label(''), 0, 0, 3, 1)
        voorbeeld_grid.attach(self.kleurlabel, 1, 1, 1, 1)
        voorbeeld_grid.attach(Gtk.Label(''), 0, 2, 3, 1)
        voorbeeld_frame.add(voorbeeld_grid)

        grid.attach(Gtk.Label("Kastcode tekst", halign=Gtk.Align.END), 0, 0, 1, 1)
        grid.attach(self.code_input, 1, 0, 5, 1)

        grid.attach(Gtk.Label("Tekstkleur", halign=Gtk.Align.END), 0, 1, 1, 1)
        grid.attach(self.kleur_letters, 1, 1, 1, 1)

        grid.attach(Gtk.Label("Achtergrondkleur", halign=Gtk.Align.END), 0, 2, 1, 1)
        grid.attach(self.kleur_achtergrond, 1, 2, 1, 1)

        grid.attach(voorbeeld_frame, 6, 0, 1, 3)
        self.get_content_area().add(grid)

        if code_id:
            kastcode = self.db.kastcode(code_id)
            self.set_kastcode(
                    kastcode['code'],
                    kastcode['tekstkleur'],
                    kastcode['achtergrondkleur'],
                )
        else:
            self.tekstkleur = Gdk.RGBA()
            self.tekstkleur.parse('black')
            self.kleur_letters.set_rgba(self.tekstkleur)

            self.achtergrondkleur  = Gdk.RGBA()
            self.achtergrondkleur.parse("lightgray")
            self.kleur_achtergrond.set_rgba(self.achtergrondkleur)

            self.color_change()

        self.show_all()

    def on_text_changed(self, entry):
        self.code = entry.get_text()
        self.kleurlabel.set_text(self.code)

    def color_change(self):
        fg = rgba2hex(self.tekstkleur)
        bg = rgba2hex(self.achtergrondkleur)
        css_content = sample_css.format(fg=fg, bg=bg)
        self._css.load_from_data(css_content.encode())

    def on_color_set(self, button):
        rgba = button.get_rgba()
        if button is self.kleur_letters:
            self.tekstkleur = rgba
        elif button is self.kleur_achtergrond:
            self.achtergrondkleur = rgba
        self.color_change()

    def set_kastcode(self, code, tekstkleur, achtergrondkleur):
        self.code_input.set_text(code)

        self.tekstkleur = Gdk.RGBA()
        self.tekstkleur.parse(tekstkleur)
        self.kleur_letters.set_rgba(self.tekstkleur)

        self.achtergrondkleur = Gdk.RGBA()
        self.achtergrondkleur.parse(achtergrondkleur)
        self.kleur_achtergrond.set_rgba(self.achtergrondkleur)

        self.color_change()

    def get_code(self):
        return self.code_input.get_text()

    def get_tekstkleur(self):
        return self.tekstkleur.to_string()

    def get_achtergrondkleur(self):
        return self.achtergrondkleur.to_string()

    def get_data(self):
        data = dict()
        data["code"] = self.code
        data["tekstkleur"] = self.tekstkleur.to_string()
        data["achtergrondkleur"] = self.achtergrondkleur.to_string()
        return data
