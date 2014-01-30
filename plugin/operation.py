#coding=utf-8
__author__ = 'Michal Petrovič'

from parameter import *

import re
from lxml import etree


class Operation:

    ATRIBUTES = (
        ("name", "name"),
        ("scope", "visibility",
            {
                "private": "Private",
                "public": "Public",
                "protected": "Protected"
            }
         ),
        ("static", "ownerScope",
            {
                "classifier": "True",
                "instance": "False"
            }
         ),
        ("abstract", "isAbstract",
            {
                "true": "True",
                "false": "False"
            }
         )
    )

    TAGGED_VALUES = (
        ("note", "documentation", lambda x: re.sub("<(.*?)>", '', x or "")),
    )

    CHILDREN_NODES = (
        ("stereotype", "UML:ModelElement.stereotype/UML:Stereotype/@name"),
    )

    def __init__(self, lxml_element, xpath):
        self.lxml_element = lxml_element
        self.xpath = xpath

        self.values = {}
        self.parameters = []

        self.xmi_file = None
        self.parent_reference = None
        self.position = None

    def read(self, xmi_file):
        self.xmi_file = xmi_file

        self._read_xml_attributes()
        self._read_tagged_values()
        self._read_children_nodes()
        self._read_parameters()

    def write(self, parent_reference):
        self.parent_reference = parent_reference
        self._write_properties()
        self._write_parameters()

    def _read_xml_attributes(self):
        for a in Operation.ATRIBUTES:
                try:
                    attribute_value = self.lxml_element.attrib.get(a[1])

                    if attribute_value:
                        if len(a) == 2:
                            value = attribute_value
                        elif len(a) == 3 and callable(a[2]):
                            value = a[2](attribute_value)
                        elif len(a) == 3 and not callable(a[2]):
                            value = a[2][attribute_value]

                        self.values[a[0]] = value
                except KeyError:
                    print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                    continue

    def _read_tagged_values(self):
        pos = self.position = self.lxml_element.xpath("UML:ModelElement.taggedValue/UML:TaggedValue[@tag='" + "position" + "']/@value", namespaces=self.xpath[1])
        if pos:
            self.position = pos[0]

        for a in Operation.TAGGED_VALUES:
            try:
                tag_value = self.lxml_element.xpath(
                    "UML:ModelElement.taggedValue/UML:TaggedValue[@tag='" + a[1] + "']/@value",
                    namespaces=self.xpath[1]
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
                print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                continue

    def _read_children_nodes(self):
        for a in Operation.CHILDREN_NODES:
            try:
                node_value = self.lxml_element.xpath(a[1], namespaces=self.xpath[1])

                if node_value:
                    if len(a) == 2:
                        value = node_value[0]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](node_value[0])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][node_value[0]]

                    self.values[a[0]] = value
            except KeyError:
                print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                continue

    def _read_parameters(self):
        parameters = self.lxml_element.xpath("UML:BehavioralFeature.parameter/UML:Parameter", namespaces=self.xpath[1])

        for parameter in parameters:
            new_parameter = Parameter(parameter, (etree.ElementTree(self.lxml_element).getpath(parameter), self.xpath[1]))

            if parameter.attrib["kind"] == "return":
                new_parameter.xmi_file = self.xmi_file
                new_parameter._read_data_type()
                self.values["rtype"] = new_parameter.values.get("type")
            else:
                new_parameter.read(self.xmi_file)
                self.parameters.append(new_parameter)

    def _write_properties(self):
        for a in self.values:
            self.parent_reference.values['operations[' + str(self.position) + '].' + a] = (self.values[a] or '')

    def _write_parameters(self):
        if self.parameters:
            if sorted([x.position for x in self.parameters]) != range(len(self.parameters)):
                get_position = lambda y: str(self.parameters.index(y))
            else:
                self.parameters.sort(key=lambda y: int(y.position))
                get_position = lambda y: str(y.position)

            for parameter in self.parameters:
                parameter.position = get_position(parameter)

                self.parent_reference.append_item('operations[' + str(self.position) + '].parameters[' + parameter.position + ']')
                parameter.write(self.parent_reference, self.position)