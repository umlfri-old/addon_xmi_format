#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree


class Diagram:

    ATRIBUTES = (
        ("name", "name"),
    )

    TAGGED_VALUES = (
        ("note", "documentation"),

    )

    def __init__(self, parent, reference, lxml_element, prefix):
        self.parent = parent
        self.reference = reference
        self.lxml_element = lxml_element
        self.prefix = prefix

        self._diagram_elements_wraper = None
        self.element_id = "D-" + self.reference._Diagram__id

    def write(self):
        self._write_xml_attributes()
        self._write_tagged_values()
        self._write_diagram_elements()
        self._write_diagram_connections()

    def _write_xml_attributes(self):
        self.lxml_element.set("xmi.id", self.element_id)
        self.lxml_element.set("owner", "E-" + self.parent._ElementObject__id)

        for a in Diagram.ATRIBUTES:
            try:
                if dict(self.reference.all_values).get(a[0]):
                    if len(a) == 2:
                        value = self.reference.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.reference.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.reference.values[a[0]]]

                    self.lxml_element.set(a[1], value)
            except KeyError:
                print "Attribute " + a[1] + " for diagram is not available or supported!"
                continue

    def _write_tagged_values(self):
        wrap_node = None
        for a in Diagram.TAGGED_VALUES:
            try:
                if dict(self.reference.all_values).get(a[0]):
                    if wrap_node is None:
                        wrap_node = etree.SubElement(self.lxml_element, self.prefix + "ModelElement.taggedValue")

                    if len(a) == 2:
                        value = self.reference.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.reference.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.reference.values[a[0]]]

                    etree.SubElement(wrap_node, self.prefix + "TaggedValue", tag=a[1], value=value)
            except KeyError:
                print "Tagged value " + a[1] + " for " + (self.reference.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_diagram_elements(self):
        seqno = 0
        for element in self.reference.elements:
            if self._diagram_elements_wraper is None:
                self._diagram_elements_wraper = etree.SubElement(self.lxml_element, self.prefix + "Diagram.element")

            diagram_element = etree.SubElement(self._diagram_elements_wraper, self.prefix + "DiagramElement")

            geometry = "Left=" + str(element.square[0][0]) + \
                       ";Top=" + str(element.square[0][1]) + \
                       ";Right=" + str(element.square[1][0]) + \
                       ";Bottom=" + str(element.square[1][1])

            diagram_element.set("geometry", geometry)
            diagram_element.set("subject", "E-" + element.object._ElementObject__id)
            diagram_element.set("seqno", str(seqno))

            seqno += 1

    def _write_diagram_connections(self):
        for element in self.reference.connections:
            if self._diagram_elements_wraper is None:
                self._diagram_elements_wraper = etree.SubElement(self.lxml_element, self.prefix + "Diagram.element")

            diagram_element = etree.SubElement(self._diagram_elements_wraper, self.prefix + "DiagramElement")
            diagram_element.set("subject", "C-" + element.object._ConnectionObject__id)