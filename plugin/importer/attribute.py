#coding=utf-8
__author__ = 'Michal Petrovič'

import re


class Attribute:

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
         )
    )

    TAGGED_VALUES = (
        ("note", "description", lambda x: re.sub("<(.*?)>", '', x or "")),
    )

    CHILDREN_NODES = (
        ("stereotype", "UML:ModelElement.stereotype/UML:Stereotype/@name"),
        ("default", "UML:Attribute.initialValue/UML:Expression/@body")
    )

    def __init__(self, lxml_element):
        self.lxml_element = lxml_element
        self.values = {}

        self.position = None
        self.xmi_file = None
        self.parent_reference = None

    def read(self, xmi_file):
        self.xmi_file = xmi_file

        self._read_xml_attributes()
        self._read_tagged_values()
        self._read_children_nodes()
        self._read_data_type()

    def write(self, parent_reference):
        self.parent_reference = parent_reference

        self._write_properties()

    def _read_xml_attributes(self):
        for a in Attribute.ATRIBUTES:
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
        pos = self.lxml_element.xpath("UML:ModelElement.taggedValue/UML:TaggedValue[@tag='" + "position" + "']/@value", namespaces=self.xmi_file.nsmap)
        if pos:
            self.position = pos[0]
        
        for a in Attribute.TAGGED_VALUES:
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
                print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                continue

    def _read_children_nodes(self):
        for a in Attribute.CHILDREN_NODES:
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
                print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                continue

    def _read_data_type(self):
        type_id = self.lxml_element.attrib.get("type")
        if not type_id:
            type_id = self.lxml_element.xpath("UML:StructuralFeature.type/UML:Classifier/@*", namespaces=self.xmi_file.nsmap)
            if type_id:
                type_id = type_id[0]
            else:
                return

        type_name = self.xmi_file.xpath("//UML:DataType[@xmi.id='" + type_id + "']/@name", namespaces=self.xmi_file.nsmap)
        if not type_name:
            type_name = self.xmi_file.xpath("//*[@xmi.id='" + type_id + "']/@name", namespaces=self.xmi_file.nsmap)
            if type_name:
                type_name = type_name[0]
            else:
                return

        self.values["type"] = type_name[0]

    def _write_properties(self):
        for a in self.values:
            self.parent_reference.values['attributes['+str(self.position)+'].'+a]=(self.values[a] or '')