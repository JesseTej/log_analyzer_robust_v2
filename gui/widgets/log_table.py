import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from log_analyzer_backend.utils.time_utils import format_timestamp

class LogTable(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_vexpand(True)

        # Columns: Timestamp, Level, SIP, DIP, Message, Source
        self.model = Gtk.ListStore(str, str, str, str, str, str)
        self.filter = self.model.filter_new()
        self.filter.set_visible_func(self.filter_func)

        self.treeview = Gtk.TreeView(model=self.filter)

        column_titles = ["Timestamp", "Level", "SIP", "DIP", "Message", "Source"]

        def get_level_color(level):
            return {
                "CRITICAL": "red",
                "ERROR": "darkred",
                "WARNING": "orange",
                "INFO": "green",
                "DEBUG": "blue",
                "TRACE": "grey"
            }.get(level.upper(), "black")

        for i, title in enumerate(column_titles):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)

            if title == "Level":
                # Color the "Level" text
                column.set_cell_data_func(renderer, lambda col, cell, model, iter, data:
                    cell.set_property("foreground", get_level_color(model[iter][1])))

            self.treeview.append_column(column)

        self.add(self.treeview)
        self.search_text = ""

    def filter_func(self, model, iter, data):
        if self.search_text == "":
            return True
        for i in range(4):
            value = model[iter][i]
            if self.search_text.lower() in value.lower():
                return True
        return False

    def set_search_filter(self, text):
        self.search_text = text
        self.filter.refilter()

    def populate(self, log_entries):
        self.model.clear()
        for entry in log_entries:
            self.model.append([
                format_timestamp(entry.timestamp),
                entry.level,
                getattr(entry, 'src_ip', '') or '',
                getattr(entry, 'dst_ip', '') or '',
                entry.message,
                getattr(entry, 'source', '')
            ])

    def append_entry(self, entry):
        self.model.append([
            format_timestamp(entry.timestamp),
            entry.level,
            getattr(entry, 'src_ip', '') or '',
            getattr(entry, 'dst_ip', '') or '',
            entry.message,
            getattr(entry, 'source', '')
        ])
