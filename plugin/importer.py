#coding=utf-8
__author__ = 'Michal Petrovič'

from element import *
from import_dialog import *

from lxml import etree


class Importer:

    def __init__(self, adapter, import_file):
        self.adapter = adapter
        self.root = None

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

    def _read(self):
        if self.xmi_version == "1.1":
            ns = self.xml_file.nsmap
            xpath = ("/XMI/XMI.content//*[@name]/UML:Namespace.ownedElement/UML:Package", ns)
            lxml_element = self.xml_file.xpath(xpath[0], namespaces=xpath[1])[0]
            self.root = Element(lxml_element, xpath)
            self.root.type = Dictionary.ELEMENT_TYPE[self.get_tag(lxml_element)]
            self.root.read(self.xml_file)

    def _write(self, parent_package):
        if parent_package is None:
            self._choose(self.adapter.templates, "Empty UML diagram").create_new_project()
            self.root.write(self.adapter.project.root, self)
        else:
            root_reference = parent_package.create_child_element(self.get_metamodel().elements[self.root.type])
            self.root.write(root_reference, self)

    def get_metamodel(self):
        if self.adapter.project:
            return self.adapter.project.metamodel