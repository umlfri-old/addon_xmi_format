#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree

from element import *
from diagram import *
from import_dialog import *


class Importer:

    def __init__(self, adapter, import_file):
        self.adapter = adapter

        self.root = None
        self.project_elements = {}
        self.project_connectors = []
        self.project_diagrams = []

        with open(import_file, "r") as tmp:
            self.xml_file = etree.fromstringlist(tmp.read())

        self.xmi_version = self.xml_file.xpath("/XMI/@xmi.version")[0]
        self.xmi_exporter = self.xml_file.xpath("/XMI/XMI.header/XMI.documentation/XMI.exporter")[0].text

        if self.adapter.project is not None:
            ImportDialog(self.adapter, self.start_importing)
        else:
            self.start_importing(None)

    def start_importing(self, parent_package=None):
        self._read()
        self._write(parent_package)

    def _read(self):
        if self.xmi_version == "1.1":
            ns = self.xml_file.nsmap
            xpath = ("/XMI/XMI.content//UML:Package", ns)
            lxml_element = self.xml_file.xpath(xpath[0], namespaces=xpath[1])[0]
            self.root = Element(lxml_element, xpath)
            self.root.type = Dictionary.ELEMENT_TYPE[self.get_tag(lxml_element)]
            self.root.read(self.xml_file, self)
            self._read_diagrams()

    def _read_diagrams(self):
        diagrams = self.xml_file.xpath("/XMI/XMI.content/UML:Diagram", namespaces=self.xml_file.nsmap)

        for diagram in diagrams:
            if diagram.get("diagramType") in Dictionary.DIAGRAM_TYPE:
                new_diagram = Diagram(diagram, (etree.ElementTree(self.xml_file).getpath(diagram), self.xml_file.nsmap))
                new_diagram.type = Dictionary.DIAGRAM_TYPE[diagram.get("diagramType")]
                new_diagram.read(self.xml_file)
                self.project_diagrams.append(new_diagram)

    def _write_diagrams(self):
        if self.project_diagrams:
            for diagram in self.project_diagrams:
                if diagram.parent_element_id in self.project_elements:
                    new_diagram = self.project_elements[diagram.parent_element_id].create_diagram(self.get_metamodel().diagrams[diagram.type])
                    diagram.write(new_diagram, self)

    def _write(self, parent_package):
        if parent_package is None:
            self._choose(self.adapter.templates, "Empty UML diagram").create_new_project()
            self.root.write(self.adapter.project.root)
        else:
            root_reference = parent_package.create_child_element(self.get_metamodel().elements[self.root.type])
            self.root.write(root_reference)
        self.project_elements[self.root.element_id] = self.root.reference
        self._write_connectors()
        self._write_diagrams()

    def _write_connectors(self):
        for connector in self.project_connectors:
            if connector.source_id not in self.project_elements or connector.dest_id not in self.project_elements:
                continue
            source = self.project_elements[connector.source_id]
            dest = self.project_elements[connector.dest_id]

            try:
                new_connector = source.connect_with(dest, self.get_metamodel().connections[connector.type])
            except Exception as e:
                if "Unknown exception" in e.message:
                    print "Connector type" + connector.type + " is not supported for " + \
                          source.name + '(' + source.type.name + ')' + \
                          " or " + dest.name + '(' + dest.type.name + ") type of element!"
                    continue
            connector.write(new_connector)

    def get_metamodel(self):
        if self.adapter.project:
            return self.adapter.project.metamodel

    def _choose(self, sequence, name):
        for x in sequence:
            if x.name == name:
                return x

    def get_tag(self, element):
        tag = element.tag
        if '}' in tag:
            ns, local = tag.split('}', 1)
            return local
        else:
            return tag