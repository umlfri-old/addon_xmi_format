#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree
import datetime

from element import *
from export_dialog import *


class Exporter:

    def __init__(self, adapter, export_file):
        self.adapter = adapter
        self.export_file = export_file

        self.root_element = None
        self.content = None
        self.content_children = None
        self.model_root = None
        self.prefix = None

        self.project_diagrams = {}
        self.project_data_types = {}

        if self.adapter.project:
            ExportDialog(self.adapter, self.start_exporting)
        else:
            self.start_exporting()

    def _create_new_document(self):
        self.prefix = "{http://www.omg.org/spec/UML/1.3}"

        self.root_element = etree.Element("XMI", {
            "xmi.version": "1.1",
            "timestamp": unicode(datetime.datetime.now())
        }, nsmap={"UML": "http://www.omg.org/spec/UML/1.3"})

        header = etree.SubElement(self.root_element, "XMI.header")
        doc = etree.SubElement(header, "XMI.documentation")
        etree.SubElement(doc, "XMI.exporter").text = "UML .FRI"
        etree.SubElement(doc, "XMI.exporterVersion").text = "1.0"

        self.content = etree.SubElement(self.root_element, "XMI.content")
        model = etree.SubElement(self.content, self.prefix + "Model")
        self.content_children = etree.SubElement(model, self.prefix + "Namespace.ownedElement")
        self.model_root = etree.SubElement(self.content_children, self.prefix + "Package")
        return self.model_root

    def start_exporting(self, parent_package=None):
        self._create_new_document()
        self._write(parent_package)

    def _write(self, parent_package):
        Element(parent_package or self.adapter.project.root, self.model_root, self.prefix, self).write()

        xml_document = etree.ElementTree(self.root_element)
        with open(self.export_file, 'w') as f:
            xml_document.write(f, encoding="UTF-8", xml_declaration=True, pretty_print=True)

    def _choose(self, sequence, name):
        for x in sequence:
            if x.name == name:
                return x

