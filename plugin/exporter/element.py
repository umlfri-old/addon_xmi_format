#coding=utf-8
__author__ = 'Michal Petrovič'

from attribute import *
from operation import *
from dictionary import *
from connector import *


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

    def __init__(self, parent, reference, lxml_element, prefix, exporter):
        self.parent = parent
        self.reference = reference
        self.lxml_element = lxml_element
        self.prefix = prefix
        self.exporter = exporter

        self.children_wraper = None
        self.connector_wraper = None

        self.children = []
        self.connectors = []

        self.type = None
        self.xmi_file = None
        self.element_id = "E-" + self.reference.__id__

        self._read_diagrams()

    def write(self):
        self._write_xml_attributes()
        self._write_tagged_values()
        self._write_children_nodes()
        self._write_childrens()
        self._write_attributes()
        self._write_operations()
        self._write_connectors()

    def _write_childrens(self):
        for child in self.reference.children:
            if self.children_wraper is None:
                self.children_wraper = etree.SubElement(self.lxml_element, self.prefix + "Namespace.ownedElement")
            try:
                if isinstance(Dictionary.ELEMENT_TYPE.get(child.type.name), tuple):
                    elm_type = Dictionary.ELEMENT_TYPE[child.type.name]
                    new_node = etree.SubElement(self.children_wraper, self.prefix + elm_type[0], kind=unicode(elm_type[1]))
                else:
                    new_node = etree.SubElement(self.children_wraper, self.prefix + Dictionary.ELEMENT_TYPE[child.type.name])

                new_element = Element(self, child, new_node, self.prefix, self.exporter)
                self.children.append(new_node)
                new_element.write()
            except KeyError:
                print "Element " + child.name or child.type.name + "is not supported."
                continue

    def _write_xml_attributes(self):
        self.lxml_element.set("xmi.id", self.element_id)
        self.lxml_element.set("namespace", self.lxml_element.xpath("(ancestor::*/@xmi.id)[last()]", namespaces=self.lxml_element.nsmap)[0])

        for a in Element.ATRIBUTES:
            try:
                if dict(self.reference.all_values).get(a[0]):
                    if len(a) == 2:
                        value = self.reference.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.reference.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.reference.values[a[0]]]

                    self.lxml_element.set(a[1], unicode(value))
            except KeyError:
                print "Attribute " + a[1] + " for " + (self.reference.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_tagged_values(self):
        wrap_node = None
        for a in Element.TAGGED_VALUES:
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

                    etree.SubElement(wrap_node, self.prefix + "TaggedValue", tag=unicode(a[1]), value=unicode(value))
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
                            wrap_node.set(path_node[1:], unicode(value))
            except KeyError:
                print "Children node value " + a[1] + " for " + (self.reference.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_attributes(self):
        attr_number = dict(self.reference.all_values).get("attributes.@length")
        wrap_node = (self.lxml_element.xpath("UML:Classifier.feature", namespaces=self.lxml_element.nsmap) or (None,))[0]
        if attr_number > 0:
            if wrap_node is None:
                wrap_node = etree.SubElement(self.lxml_element, self.prefix + "Classifier.feature")

            for position in range(attr_number):
                new_node = etree.SubElement(wrap_node, self.prefix + "Attribute")
                Attribute(self.reference, new_node, position, self.prefix, self.exporter).write()

    def _write_operations(self):
        operations_number = dict(self.reference.all_values).get("operations.@length")
        wrap_node = (self.lxml_element.xpath("UML:Classifier.feature", namespaces=self.lxml_element.nsmap) or (None,))[0]
        if operations_number > 0:
            if wrap_node is None:
                wrap_node = etree.SubElement(self.lxml_element, self.prefix + "Classifier.feature")

            for position in range(operations_number):
                new_node = etree.SubElement(wrap_node, self.prefix + "Operation")
                Operation(self.reference, new_node, position, self.prefix, self.exporter).write()

    def _write_connectors(self):
        wrapper = None
        for connector in self.reference.connections:
            if connector not in self.exporter.exported_connectors:
                if wrapper is None:
                    if self.parent.connector_wraper is None:
                        wrapper = self.parent.children_wraper
                    else:
                        wrapper = self.parent.connector_wraper

                try:
                    elm_type = Dictionary.CONNECTION_TYPE[connector.type.name]
                    if isinstance(elm_type, tuple):
                        if elm_type[0] == "Association":
                            new_node = etree.SubElement(wrapper, self.prefix + unicode(elm_type[0]))
                            kind = elm_type[1]
                        else:
                            if self.parent.connector_wraper is None:
                                for child_element in self.parent.children:
                                    self.parent.children_wraper.remove(child_element)

                                for child_connector in self.parent.connectors:
                                    self.parent.children_wraper.remove(child_connector)

                                tmp_wrapper0 = etree.SubElement(self.parent.children_wraper, self.prefix + unicode(elm_type[1]))
                                tmp_wrapper1 = etree.SubElement(tmp_wrapper0, self.prefix + "StateMachine.top")
                                tmp_wrapper1 = etree.SubElement(tmp_wrapper1, self.prefix + "CompositeState")
                                self.parent.children_wraper = etree.SubElement(tmp_wrapper1, self.prefix + "CompositeState.subvertex")

                                wrapper = self.parent.connector_wraper = etree.SubElement(tmp_wrapper0, self.prefix + "StateMachine.transitions")

                                for child_element in self.parent.children:
                                    self.parent.children_wraper.append(child_element)

                                for child_connector in self.parent.connectors:
                                    self.parent.connector_wraper.append(child_connector)

                            new_node = etree.SubElement(wrapper, self.prefix + unicode(elm_type[0]))
                            kind = None
                    else:
                        new_node = etree.SubElement(wrapper, self.prefix + unicode(elm_type))
                        kind = None

                    new_connector = Connector(connector, new_node, kind, self.prefix, self.exporter)
                    self.exporter.exported_connectors.append(connector)
                    self.connectors.append(new_node)
                    new_connector.write()
                except KeyError:
                    continue

    def _read_diagrams(self):
        for diagram in self.reference.diagrams:
            if diagram not in self.exporter.project_diagrams:
                self.exporter.project_diagrams[diagram] = self.reference