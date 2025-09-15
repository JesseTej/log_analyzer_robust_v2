# gui/main.py

from gi.repository import Gtk
from gui.main_window import MainWindow
from log_analyzer_backend.log_loader import load_log_file

def main():
    win = MainWindow()

    # Example log loading
    logs = load_log_file("sample.log")  # Should return list of LogEntry
    win.load_logs(logs)

    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
