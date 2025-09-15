import threading
import time
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from datetime import datetime

from gui.widgets.log_table import LogTable
from log_analyzer_backend.parsers.parser_factory import get_parser
from log_analyzer_backend.backend import LogAnalyzerBackend
from log_analyzer_backend.utils.time_utils import format_timestamp


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Log Analyzer")
        self.set_default_size(800, 600)
        self.show_details_check = Gtk.CheckButton(label='Show details (IPs/Ports/Domains)')
        self.show_details_check.set_active(True)
        self.show_details_check.connect('toggled', self.on_show_details_toggled)
        # NOTE: you might need to place this widget into a container in the UI layout
        self.set_border_width(10)

        self.last_loaded_path = None
        self.backend_parser = None
        self.tailing_active = False
        self.backend = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        load_button = Gtk.Button(label="Load Log")
        load_button.connect("clicked", self.on_load_clicked)
        toolbar.pack_start(load_button, False, False, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search logs...")
        self.search_entry.connect("changed", self.on_search_changed)
        toolbar.pack_start(self.search_entry, True, True, 0)

        self.start_time_entry = Gtk.Entry()
        self.start_time_entry.set_placeholder_text("Start time (YYYY-MM-DD HH:MM:SS)")
        toolbar.pack_start(self.start_time_entry, False, False, 0)

        self.end_time_entry = Gtk.Entry()
        self.end_time_entry.set_placeholder_text("End time (YYYY-MM-DD HH:MM:SS)")
        toolbar.pack_start(self.end_time_entry, False, False, 0)

        filter_button = Gtk.Button(label="Filter Logs")
        filter_button.connect("clicked", self.on_search_button_clicked)
        toolbar.pack_start(filter_button, False, False, 0)

        self.tail_button = Gtk.ToggleButton(label="Start Tailing")
        self.tail_button.connect("toggled", self.on_tail_toggled)
        toolbar.pack_start(self.tail_button, False, False, 0)

        vbox.pack_start(toolbar, False, False, 0)

        # Your LogTable instance
        self.table = LogTable()
        vbox.pack_start(self.table, True, True, 0)

        self.add(vbox)
        self.show_all()

    def on_load_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Open Log File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            dialog.destroy()

            try:
                parser = get_parser(filepath)
                entries = parser.parse()

                self.backend = LogAnalyzerBackend()
                self.backend.load_logs(entries)
                self.table.populate(entries)

                self.last_loaded_path = filepath
                self.backend_parser = parser._parse_line  # For tailing

            except Exception as e:
                self.show_error(str(e))
        else:
            dialog.destroy()

    def on_search_changed(self, entry):
        text = entry.get_text()
        self.table.set_search_filter(text)

    def show_error(self, message):
        error_dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Failed to load log file.",
        )
        error_dialog.format_secondary_text(message)
        error_dialog.run()
        error_dialog.destroy()

    def on_tail_toggled(self, button):
        if button.get_active():
            if not self.last_loaded_path or not self.backend_parser:
                self.show_error("No log file loaded to tail.")
                GLib.idle_add(self.tail_button.set_active, False)
                return

            button.set_label("Stop Tailing")
            self.tailing_active = True
            self.tail_thread = threading.Thread(target=self.tail_log_file, daemon=True)
            self.tail_thread.start()
        else:
            button.set_label("Start Tailing")
            self.tailing_active = False

    def tail_log_file(self):
        try:
            with open(self.last_loaded_path, "r") as f:
                f.seek(0, os.SEEK_END)  # Move to end

                while self.tailing_active:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue

                    entry = self.backend_parser(line.strip())
                    if entry:
                        GLib.idle_add(self.table.append_entry, entry)

        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
            GLib.idle_add(self.tail_button.set_active, False)

    def on_search_button_clicked(self, button):
        keyword = self.search_entry.get_text()
        start_time_str = self.start_time_entry.get_text()
        end_time_str = self.end_time_entry.get_text()

        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None
        except ValueError:
            self.show_error("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
            return

        results = self.backend.filter_logs(keyword=keyword, start_time=start_time, end_time=end_time)
        self.table.populate(results)


    def on_show_details_toggled(self, widget):
        show = widget.get_active()
        try:
            tv = self.table.treeview
            for idx in range(4, 9):
                col = tv.get_column(idx)
                if col:
                    col.set_visible(show)
        except Exception:
            pass
