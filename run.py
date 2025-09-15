import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gui.main_window import MainWindow

def main():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()

