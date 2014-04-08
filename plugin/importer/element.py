#coding=utf-8
__author__ = 'Michal Petrovič'

import re

from lxml import etree

from attribute import *
from operation import *
from dictionary import *
from connector import *


class Element:

    ATRIBUTES = (
        ("name", "name"),
        ("abstract", "isAbstract",
            {
                'false': "False",
                'true': "True"
            }
         ),
        ("scope", "visibility",
            {
                "private": "Private",
                "public": "Public",
                "protected": "Protected"
            }
         )
    )

    TAGGED_VALUES = (
        ("note", "documentation", lambda x: re.sub("<(.*?)>", '', x or "")),

    )

    CHILDREN_NODES = (
        ("stereotype", "UML:ModelElement.stereotype/UML:Stereotype/@name")
    )

    def __init__(self, lxml_element):
        self.lxml_element = lxml_element

        self.diagrams = []
        self.childrens = []
        self.connections = []
        self.appears = []
        self.atributes = []
        self.operations = []
        self.values = {}

        self.type = None
        self.xmi_file = None
        self.element_id = None
        self.reference = None
        self.importer = None

    def read(self, xmi_file, importer):
        self.xmi_file = xmi_file
        self.importer = importer

        self._read_xml_attributes()
        self._read_tagged_values()
        self._read_children_nodes()
        self._read_childrens()
        self._read_attributes()
        self._read_operations()

    def write(self, reference):
        self.reference = reference

        self._write_properties()
        self._write_children()
        self._write_attributes()
        self._write_operations()

    def _read_childrens(self):
        owned_elements = self.lxml_element.xpath("UML:Namespace.ownedElement/*", namespaces=self.xmi_file.nsmap) +\
                        self.lxml_element.xpath("UML:Namespace.ownedElement/UML:ActivityGraph/UML:StateMachine.top/UML:CompositeState/UML:CompositeState.subvertex/*", namespaces=self.xmi_file.nsmap) +\
                        self.lxml_element.xpath("UML:Namespace.ownedElement/UML:StateMachine/UML:StateMachine.top/UML:CompositeState/UML:CompositeState.subvertex/*", namespaces=self.xmi_file.nsmap)

        if owned_elements:
            for child in owned_elements:
                if ((child.get("kind") and (self._get_tag(child), child.get("kind"))) or self._get_tag(child)) in Dictionary.ELEMENT_TYPE:
                    new_element = Element(child)
                    new_element.type = Dictionary.ELEMENT_TYPE[((child.get("kind") and (self._get_tag(child), child.get("kind"))) or self._get_tag(child))]
                    new_element.read(self.xmi_file, self.importer)
                    self.childrens.append(new_element)

            self._read_connectors(owned_elements)

    def _read_xml_attributes(self):
        self.element_id = self.lxml_element.attrib["xmi.id"]

        for a in Element.ATRIBUTES:
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
        for a in Element.TAGGED_VALUES:
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

    def _read_children_nodes(self):
        for a in Element.TAGGED_VALUES:
            try:

                node_value = self.lxml_element.xpath(a[1], namespaces=self.xmi_file.nsmap)

                if node_value:
                    if len(a) == 2:
                        value = node_value[0]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](node_value[0])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][node_value[0]]

                    self.values[a[0]] = value
            except KeyError:
                print "Children node value " + a[1] + " for " + (self.values.get("name") or self.type) + " is not available or supported!"
                continue

    def _read_attributes(self):
        attributes = self.lxml_element.xpath("UML:Classifier.feature/UML:Attribute", namespaces=self.xmi_file.nsmap)

        for attribute in attributes:
            new_attribute = Attribute(attribute)
            new_attribute.read(self.xmi_file)
            self.atributes.append(new_attribute)

    def _read_operations(self):
        operations = self.lxml_element.xpath("UML:Classifier.feature/UML:Operation", namespaces=self.xmi_file.nsmap)

        for operation in operations:
            new_operation = Operation(operation)
            new_operation.read(self.xmi_file)
            self.operations.append(new_operation)

    def _read_connectors(self, owned_element):
        owned_element += self.lxml_element.xpath("UML:Namespace.ownedElement/UML:ActivityGraph/UML:StateMachine.transitions/*", namespaces=self.xmi_file.nsmap) + \
            self.lxml_element.xpath("UML:Namespace.ownedElement/UML:StateMachine/UML:StateMachine.transitions/*", namespaces=self.xmi_file.nsmap)

        for connector in owned_element:
            possible_type = [
                self._get_tag(connector),
                (self._get_tag(connector), self._get_tag((connector.xpath("../..", namespaces=self.xmi_file.nsmap) or ("",))[0])),
                (self._get_tag(connector), (connector.xpath("*/*[@aggregation!='none']/@aggregation", namespaces=self.xmi_file.nsmap) or ("",))[0]),
                (self._get_tag(connector), connector.xpath("*/*/@aggregation!='none'", namespaces=self.xmi_file.nsmap) or "normal")
            ]

            #check for use case association
            end_id = connector.xpath("UML:Association.connection/UML:AssociationEnd/@type", namespaces=self.xmi_file.nsmap)
            end_type = [(connector.xpath("//*[@xmi.id='" + x + "']", namespaces=self.xmi_file.nsmap) or ("",))[0] for x in end_id]
            if any(self._get_tag(x) in ("UseCase", "Actor") for x in end_type) and ("Association", "normal") in possible_type:
                possible_type.remove(("Association", "normal"))
                possible_type.append((self._get_tag(connector), "useCase"))

            intersection = set(Dictionary.CONNECTION_TYPE).intersection(possible_type)
            if len(intersection) == 1:
                new_connector = Connector(connector)
                new_connector.type = Dictionary.CONNECTION_TYPE.get(list(intersection)[0])
                new_connector.read(self.xmi_file)
                self.importer.project_connectors.append(new_connector)

    def _get_tag(self, element):
        tag = element.tag
        if '}' in tag:
            ns, local = tag.split('}', 1)
            return local
        else:
            return tag

    def _write_children(self):
        for a in self.childrens:
            new_child = self.reference.create_child_element(self.importer.get_metamodel().elements[a.type])
            a.write(new_child)
            self.importer.project_elements[a.element_id] = new_child

    def _write_properties(self):
        for a in self.values:
            try:
                self.reference.values[a] = (self.values[a] or '')
            except Exception as e:
                if "Invalid attribute" in e.message:
                    print "Element type: " + self.type + " do not support property " + a
                    continue
                else:
                    raise

    def _write_attributes(self):
        if self.atributes:
            if sorted([x.position for x in self.atributes]) != range(len(self.atributes)):
                get_position = lambda y: str(self.atributes.index(y))
            else:
                self.atributes.sort(key=lambda y: int(x.position))
                get_position = lambda y: str(y.position)

            for attribute in self.atributes:
                attribute.position = get_position(attribute)

                self.reference.append_item('attributes[' + attribute.position + ']')
                attribute.write(self.reference)

    def _write_operations(self):
        if self.operations:
            if sorted([x.position for x in self.operations]) != range(len(self.operations)):
                get_position = lambda y: str(self.operations.index(y))
            else:
                self.operations.sort(key=lambda y: int(y.position))
                get_position = lambda y: str(y.position)

            for operation in self.operations:
                operation.position = get_position(operation)

                self.reference.append_item('operations[' + operation.position + ']')
                operation.write(self.reference)