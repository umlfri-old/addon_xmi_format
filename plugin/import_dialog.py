#coding=utf-8
__author__ = 'Michal Petrovič'

import pygtk
pygtk.require('2.0')
import gtk


class ImportDialog:

    def __init__(self, adapter, callback):
        self._packages_set = {}
        self._treestore = gtk.TreeStore(str)
        self._make_treestore(adapter.project.root, None)

        self._dialog = gtk.Dialog("Možnosti importovania", None, 0, None)
        self._dialog.set_size_request(300, 400)
        self._dialog.set_border_width(10)

        self._radio1 = gtk.RadioButton(None, "importovať ako nový projekt")
        self._radio2 = gtk.RadioButton(self._radio1, "importovať do zvoleného priečinka")
        self._radio1.connect("toggled", self._on_button_toggle, "radio1")
        self._radio2.connect("toggled", self._on_button_toggle, "radio2")
        self._radio1.set_active(True)

        self._separator1 = gtk.HSeparator()

        self._tree = gtk.TreeView()
        self._tree.set_enable_search(False)
        self._tree.set_model(self._treestore)
        self._tree.set_headers_visible(False)
        self._tree.get_selection().connect("changed", self._on_selection_changed)

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 0)
        self._tree.append_column(column)

        self._scroll_window = gtk.ScrolledWindow()
        self._scroll_window.add_with_viewport(self._tree)
        self._scroll_window.set_usize(-1, 200)
        self._scroll_window.set_sensitive(False)
        self._scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self._label = gtk.Label("Priečinok do ktorého sa bude importovať")
        self._label.set_alignment(0, 1)

        self._input_line = gtk.Entry()
        self._input_line.set_editable(False)
        self._input_line.set_sensitive(False)

        self._cancel_button = gtk.Button("Zrušiť")
        self._cancel_button.connect("clicked", self._on_cancel_button)
        self._ok_button = gtk.Button("Importovať")
        self._ok_button.connect("clicked", self._on_ok_button, callback)

        self._hbox = gtk.HBox(False, 0)
        self._hbox.pack_end(self._ok_button, False, False, 0)
        self._hbox.pack_end(self._cancel_button, False, False, 0)

        self._dialog.vbox.pack_start(self._radio1, False, False, 0)
        self._dialog.vbox.pack_start(self._radio2, False, False, 0)
        self._dialog.vbox.pack_start(self._separator1, False, False, 5)
        self._dialog.vbox.pack_start(self._scroll_window, True, True, 0)
        self._dialog.vbox.pack_start(self._label, True, True, 0)
        self._dialog.vbox.pack_start(self._input_line, False, False, 5)
        self._dialog.vbox.pack_end(self._hbox, False, False, 0)

        self._radio1.show()
        self._radio2.show()
        self._separator1.show()
        self._tree.show()
        self._scroll_window.show()
        self._label.show()
        self._input_line.show()
        self._cancel_button.show()
        self._ok_button.show()
        self._hbox.show()

        self._dialog.show()
        self._dialog.run()

    def _make_treestore(self, element, parent_tree):
        if element.type.name == "Package":
            row = self._treestore.append(parent_tree, [element.name])
            self._packages_set[self._treestore.get_path(row)] = element

            for x in element.children:
                if x.type.name == "Package":
                    self._make_treestore(x, row)

    def _on_selection_changed(self, tree_selection):
        (model, tree_iter) = tree_selection.get_selected()
        value = model.get_value(tree_iter, 0)
        self._input_line.set_text(value)

    def _on_button_toggle(self, button, data):
        if data == "radio1" and button.get_active():
            self._input_line.set_sensitive(False)
            self._scroll_window.set_sensitive(False)
            self._label.set_sensitive(False)
            self._input_line.set_text("")

        elif data == "radio2" and button.get_active():
            self._input_line.set_sensitive(True)
            self._scroll_window.set_sensitive(True)
            self._label.set_sensitive(True)

    def _on_cancel_button(self, button, data=None):
        self._dialog.destroy()

    def _on_ok_button(self, button, callback):
        if self._radio2.get_active():
            callback(self._packages_set[self._treestore.get_path(
                self._tree.get_selection().get_selected()[1])])
        else:
            callback()
        self._dialog.destroy()