#coding=utf-8
__author__ = 'Michal Petrovič'

import re


class Diagram:

    ATRIBUTES = (
        ("name", "name"),
    )

    TAGGED_VALUES = (
        ("note", "documentation", lambda x: re.sub("<(.*?)>", '', x or "")),

    )

    def __init__(self, lxml_element):
        self.lxml_element = lxml_element

        self.showed_objects = []
        self.values = {}
        self.type = None

        self.xmi_file = None
        self.element_id = None
        self.reference = None
        self.importer = None
        self.parent_element_id = None

    def read(self, xmi_file):
        self.xmi_file = xmi_file

        self._read_xml_attributes()
        self._read_tagged_values()
        self._read_elements()

    def write(self, reference, importer):
        self.reference = reference
        self.importer = importer

        self._write_properties()
        self._write_elements()

    def _read_xml_attributes(self):
        self.element_id = self.lxml_element.attrib["xmi.id"]
        self.parent_element_id = self.lxml_element.attrib["owner"]

        for a in Diagram.ATRIBUTES:
                try:
                    if len(a) == 2:
                        value = self.lxml_element.attrib[a[1]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.lxml_element.attrib[a[1]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.lxml_element.attrib[a[1]]]

                    self.values[a[0]] = value
                except KeyError:
                    print "Attribute " + a[1] + " for " + (self.values.get("name") or self.type) + " is not available or supported!"
                    continue

    def _read_tagged_values(self):
        for a in Diagram.TAGGED_VALUES:
            try:
                tag_value = self.lxml_element.xpath(
                    "UML:ModelElement.taggedValue/UML:TaggedValue[@tag='" + a[1] + "']/@value",
                    namespaces=self.xmi_file.nsmap
                )

                if tag_value:
                    if len(a) == 2:
                        value = tag_value[0]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](tag_value[0])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][tag_value[0]]

                    self.values[a[0]] = value
            except KeyError:
                print "Tagged value " + a[1] + " for " + (self.values.get("name") or self.type) + " is not available or supported!"
                continue

    def _read_elements(self):
        diagram_elements = self.lxml_element.xpath("UML:Diagram.element/UML:DiagramElement", namespaces=self.xmi_file.nsmap)

        for element in diagram_elements:
            self.showed_objects.append(element.get("subject"))

    def _write_elements(self):
        if self.showed_objects:
            for identificator in self.showed_objects:
                element = self.importer.project_elements.get(identificator) or \
                    ([item.reference for item in self.importer.project_connectors if item.element_id == identificator] or (None,))[0]

                if element:
                    if not (self.reference.get_element(element) or self.reference.get_connection(element)):
                        element.show_in(self.reference)

    def _write_properties(self):
        for a in self.values:
            self.reference.values[a] = (self.values[a] or '')
