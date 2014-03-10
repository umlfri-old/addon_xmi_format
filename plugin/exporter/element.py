#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree
from attribute import *


from dictionary import *

class Element:

    ATRIBUTES = (
        ("name", "name"),
        ("abstract", "isAbstract",
            {
                "False": "false",
                "True": "true"
            }
         ),
        ("scope", "visibility",
            {
                "Private": "private",
                "Protected": "protected",
                "Public": "public"
            }
         )
    )

    TAGGED_VALUES = (
        ("note", "documentation"),

    )

    CHILDREN_NODES = (
        ("stereotype", "ModelElement.stereotype/Stereotype/@name")
    )

    def __init__(self, reference, lxml_element, prefix, exporter):
        self.reference = reference
        self.lxml_element = lxml_element
        self.prefix = prefix
        self.exporter = exporter

        self.type = None
        self.xmi_file = None
        self.element_id = None

    def write(self):
        self._write_xml_attributes()
        self._write_tagged_values()
        self._write_children_nodes()
        self._write_childrens()
        self._write_attributes()

    def _write_childrens(self):
        wrap_node = None
        for child in self.reference.children:
            if not wrap_node:
                wrap_node = etree.SubElement(self.lxml_element, self.prefix + "Namespace.ownedElement")
            try:
                if isinstance(Dictionary.ELEMENT_TYPE.get(child.type.name), tuple):
                    elm_type = Dictionary.ELEMENT_TYPE[child.type.name]
                    new_node = etree.SubElement(wrap_node, self.prefix + elm_type[0], kind=elm_type[1])
                else:
                    new_node = etree.SubElement(wrap_node, self.prefix + Dictionary.ELEMENT_TYPE[child.type.name])

                Element(child, new_node, self.prefix, self.exporter).write()
            except KeyError:
                continue

    def _write_xml_attributes(self):
        self.lxml_element.set("xmi.id", "ID_" + unicode(id(self.reference)))

        for a in Element.ATRIBUTES:
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
                print "Attribute " + a[1] + " for " + (self.reference.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_tagged_values(self):
        wrap_node = None
        for a in Element.TAGGED_VALUES:
            try:
                if dict(self.reference.all_values).get(a[0]):
                    if not wrap_node:
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

    def _write_children_nodes(self):
        for a in Element.CHILDREN_NODES:
            try:
                if dict(self.reference.all_values).get(a[0]):
                    if len(a) == 2:
                        value = self.reference.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.reference.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.reference.values[a[0]]]

                    wrap_node = self.lxml_element
                    path_nodes = a[1].split('/')
                    for path_node in path_nodes:
                        if path_node[0] != '@':
                            wrap_node = etree.SubElement(wrap_node, self.prefix + path_node)
                        else:
                            wrap_node.set(path_node[1:], value)
            except KeyError:
                print "Children node value " + a[1] + " for " + (self.reference.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_attributes(self):
        attr_number = dict(self.reference.all_values).get("attributes.@length")
        wrap_node = None
        if attr_number > 0:
            if not wrap_node:
                wrap_node = etree.SubElement(self.lxml_element, self.prefix + "Classifier.feature")

            for position in range(attr_number):
                new_node = etree.SubElement(wrap_node, self.prefix + "Attribute")
                Attribute(self.reference, new_node, position, self.prefix, self.exporter).write()