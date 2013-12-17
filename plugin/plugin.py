__author__ = 'janik'

from importer import Importer


def pluginMain(interface):
    interface.transaction.autocommit = True
    ft = interface.file_type_manager.register_file_type('application/xmi', 'XML Metadata Interchange')
    ft.add_extension('xmi')
    ft.add_extension('xml')
    ft.import_enabled = True
    ft.register_import_handler(lambda file_name: Importer(interface, file_name))
