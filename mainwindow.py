import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import re
import signal
from collections import deque

from boekwidget import BoekWidget
from kastcodewidget import KastcodeWidget
from categoriewidget import CategorieWidget
from persoonwidget import PersoonWidget
from uitleenwidget import UitleenWidget
from barcodeswidget import BarcodesWidget

re_isbn_char = re.compile('^[0-9]$')
re_isbn = re.compile('^[0-9]{13}$')
barcode_buf = deque((), 13)

def alarm_handler(signum, stackframe):
    barcode_buf.clear()

class About(Gtk.Label):
    def __init__(self):
        super().__init__()
        self.invalidated = False
        self.set_markup("<span size='x-large'>"
                        "<b>Boekleen</b> versie 4\n"
                        "GNU Public License (GPL)\n"
                        "© 2019 Heiko Noordhof\n"
                        "</span>")

class Stub(Gtk.Label):
    def __init__(self):
        super().__init__()
        self.set_angle(20)
        self.set_markup("<span foreground='gray' font='32' weight='bold'>Nog niet gemaakt</span>")

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(900, 600)

        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.BOTTOM)

        self.connect("key-press-event", self.on_key_press)
        signal.signal(signal.SIGALRM, alarm_handler)

        def add_tab(tabclass, tabtitle):
            widget = tabclass(self, self.props.application.db)
            self.notebook.append_page(widget, Gtk.Label(tabtitle))

        for tab in self.props.application.tabs:
            if tab == "boek": add_tab(BoekWidget, "Boeken")
            elif tab == "kastcode": add_tab(KastcodeWidget, "Kastcodes")
            elif tab == "categorie": add_tab(CategorieWidget, "Categoriën")
            elif tab == "lener": add_tab(PersoonWidget, "Leners")
            elif tab == "uitlenen": add_tab(UitleenWidget, "Uitlenen")
            elif tab == "barcodes": add_tab(BarcodesWidget, "Streepjescodes")
            else:
                print("Error: onbekende tab-naam. Hoort niet te gebeuren", file=sys.stderr)

        self.notebook.append_page(About(), Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.MENU))
        self.notebook.connect("switch-page", self.on_switch_page)
        self.add(self.notebook)

        # activeren
        #
        self.show_all()

    def invalidate(self):
        for tab in self.notebook:
            tab.invalidated = True

    def on_switch_page(self, notebook, page, page_num):
        if page.invalidated and hasattr(page, 'refresh') and callable(page.refresh):
            page.refresh()

    def on_key_press(self, win, event):
        if event.keyval == Gdk.KEY_Return:
            signal.alarm(0)
            isbn = "".join(barcode_buf)
            barcode_buf.clear()
            if re_isbn.match(isbn):  # ziet er grofweg uit als een geldig isbn?
                self.on_isbn_scan(isbn)
                return True
        else:
            try:
                key = chr(event.keyval)
            except ValueError: # een of andere rare toests combi (geluid harder, o.i.d) negeren.
                signal.alarm(0)
                barcode_buf.clear()
                return True
            if re_isbn_char.match(key):
                if len(barcode_buf) == 0:
                    signal.alarm(1)
                barcode_buf.append(key)
            else:
                signal.alarm(0)
                barcode_buf.clear()

    def on_isbn_scan(self, isbn):
        current_page = self.notebook.get_nth_page(self.notebook.get_current_page())
        if hasattr(current_page, 'on_isbn_scan') and callable(current_page.on_isbn_scan):
            current_page.on_isbn_scan(isbn)

