#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree

class Attribute:

    ATRIBUTES = (
        ("name", "name"),
        ("scope", "visibility",
            {
                "Private": "private",
                "Public": "public",
                "Protected": "protected"
            }
         ),
        ("static", "ownerScope",
            {
                "True": "classifier",
                "False": "instance"
            }
         )
    )

    TAGGED_VALUES = (
        ("note", "description"),
    )

    CHILDREN_NODES = (
        ("stereotype", "ModelElement.stereotype/Stereotype/@name"),
        ("default", "Attribute.initialValue/Expression/@body")
    )

    def __init__(self, parent_reference, lxml_element, position, prefix, exporter):
        self.parent_reference = parent_reference
        self.lxml_element = lxml_element
        self.position = position
        self.prefix = prefix
        self.exporter = exporter

        self.values = self._extract_values()
        self.element_id = "E-" + self.parent_reference._ElementObject__id + \
                          "-A-" + str(self.position)

    def _extract_values(self):
        extracted = []
        for x in self.parent_reference.all_values:
            if x[0].startswith("attributes[" + str(self.position) + "]"):
                extracted.append((x[0].replace("attributes[" + str(self.position) + "].", ''), x[1]))
        return dict(extracted)

    def write(self):
        self._write_xml_attributes()
        self._write_tagged_values()
        self._write_children_nodes()
        self._write_data_type()

    def _write_xml_attributes(self):
        self.lxml_element.set("xmi.id", self.element_id)
        self.lxml_element.set("owner", self.parent_reference._ElementObject__id)

        for a in Attribute.ATRIBUTES:
            try:
                if dict(self.values).get(a[0]):
                    if len(a) == 2:
                        value = self.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.values[a[0]]]

                    self.lxml_element.set(a[1], value)
            except KeyError:
                print "Attribute " + a[0] + " for " + (self.values["name"] or self.reference.type.name) + " is not available or supported!"
                continue

    def _write_tagged_values(self):
        wrap_node = None
        for a in Attribute.TAGGED_VALUES:
            try:
                if dict(self.values).get(a[0]):
                    if wrap_node is None:
                        wrap_node = etree.SubElement(self.lxml_element, self.prefix + "ModelElement.taggedValue")

                    if len(a) == 2:
                        value = self.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.values[a[0]]]

                    etree.SubElement(wrap_node, self.prefix + "TaggedValue", tag=a[1], value=value)
            except KeyError:
                print "Tagged value " + a[0] + " for " + (self.values["name"] or self.parent_reference.type.name) + " is not available or supported!"
                continue

    def _write_children_nodes(self):
        for a in Attribute.CHILDREN_NODES:
            try:
                if dict(self.values).get(a[0]):
                    if len(a) == 2:
                        value = self.values[a[0]]
                    elif len(a) == 3 and callable(a[2]):
                        value = a[2](self.values[a[0]])
                    elif len(a) == 3 and not callable(a[2]):
                        value = a[2][self.values[a[0]]]

                    wrap_node = self.lxml_element
                    path_nodes = a[1].split('/')
                    for path_node in path_nodes:
                        if path_node[0] != '@':
                            wrap_node = etree.SubElement(wrap_node, self.prefix + path_node)
                        else:
                            wrap_node.set(path_node[1:], value)
            except KeyError:
                print "Children node value " + a[0] + " for " + (self.values["name"] or self.parent_reference.type.name) + " is not available or supported!"
                continue

    def _write_data_type(self):
        if self.values.get("type"):
            if self.values.get("type") in self.exporter.project_data_types:
                self.lxml_element.set("type", self.exporter.project_data_types[self.values.get("type")])
            else:
                new_type_id = "TYPE-" + str(hash(self.values.get("type")))
                self.lxml_element.set("type", new_type_id)
                self.exporter.project_data_types[self.values.get("type")] = new_type_id