#coding=utf-8
__author__ = 'Michal Petrovič'

from dictionary import *
import re


class Element:

    def __init__(self, lxml_element, xpath=None):
        self.lxml_element = lxml_element
        self.xpath = xpath

        self.diagrams = []
        self.childrens = []
        self.connections = []
        self.appears = []
        self.atributes = []
        self.operations = []
        self.values = {}

        self.xmi_file = None
        self.type = None
        self.name = None
        self.element_id = None
        self.reference = None
        self.importer = None

    def read(self, xmi_file):
        self.xmi_file = xmi_file

        self._read_attributes()
        self._read_childrens()

    def write(self, reference, importer):
        self.reference = reference
        self.importer = importer

        self._write_children()

    def _read_childrens(self):
        owned_element = [x for x in self.lxml_element.getchildren() if "Namespace.ownedElement" in x.tag]
        if len(owned_element) == 1:
            children = [y for y in owned_element[0].getchildren()]

            for child in children:
                if self._get_tag(child) in Dictionary.ELEMENT_TYPE:
                    new_element = Element(child)
                    new_element.read(self.xmi_file)
                    self.childrens.append(new_element)

    def _read_attributes(self):
        self.type = self._get_tag(self.lxml_element)
        self.name = self.lxml_element.attrib["name"]
        self.element_id = self.lxml_element.attrib["xmi.id"]


    def _get_tag(self, element):
        tag = element.tag
        if '}' in tag:
            ns, local = tag.split('}', 1)
            return local
        else:
            return tag

    def _write_children(self):
        for a in self.childrens:
            print "write element " + repr(a.name)
            new_child = self.reference.create_child_element(self.importer.get_metamodel().elements[a.type])
            a.write(new_child, self.importer)