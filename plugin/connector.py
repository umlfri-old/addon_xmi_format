#coding=utf-8
__author__ = 'Michal Petrovič'

import re


class Connector:

    ATRIBUTES = (
        ("name", "name"),
        (("SRole", "DRole"), "name"),
        (("SCardinality", "DCardinality"), "multiplicity")

    )

    TAGGED_VALUES = (
        ("note", "documentation", lambda x: re.sub("<(.*?)>", '', x or "")),
        ("note", "description", lambda x: re.sub("<(.*?)>", '', x or ""))
    )

    CHILDREN_NODES = (
        ("stereotype", "UML:ModelElement.stereotype/UML:Stereotype/@name"),
        #("stereotype", "//UML:Stereotype[@modelElement='" + eval("self.element_id") + "']/@name"),
        ("guard", "UML:Transition.guard/UML:Guard/UML:Guard.expression/UML:BooleanExpression/@body"),
        (("SCardinality", "DCardinality"), "concat("
                                           "substring('', 1, number(count(UML:AssociationEnd.multiplicity) != 1)*1),"
                                           "substring("
                                           "concat(UML:AssociationEnd.multiplicity/UML:Multiplicity/UML:Multiplicity.range/UML:MultiplicityRange/@lower,"
                                           "'..',"
                                           "UML:AssociationEnd.multiplicity/UML:Multiplicity/UML:Multiplicity.range/UML:MultiplicityRange/@upper)"
                                           ", 1, number(not(count(UML:AssociationEnd.multiplicity) != 1))*50))")
    )

    SOURCE = ("type", "subtype", "client", "source", "extension", "base", "child")
    DESTINATION = ("type", "supertype", "supplier", "target", "addition", "base", "parent")



    PROPERTIES = (
        #("name", 1),
        #("stereotype", 46),
        #("note", 3,lambda x:re.sub("<(.*?)>",'',x or "")),
        ("direction", 2,
         {
             "Unspecified": "Unspecified",
             "Source -> Destination": "Source to Destination",
             "Destination -> Source": "Destination to Source",
             "Bi-Directional": "Bidirectional"
         }
         ),
        #("SCardinality", 6),
        #("DCardinality", 9),
        #("SRole", 12),
        #("DRole", 19),
        #("guard", 50),
        #("weight", 51)                                                          # nie je podporovane
    )

    def __init__(self, lxml_element, xpath):
        self.lxml_element = lxml_element
        self.xpath = xpath

        self.source_id = None
        self.dest_id = None
        self.type = None
        self.values = {}
        self.appears = []
        self.element_id = None

        self.xmi_file = None
        self.reference = None


    def read(self, xmi_file):
        self.xmi_file = xmi_file

        self._read_xml_attributes()
        self._read_tagged_values()
        self._read_children_nodes()
        self._read_direction()

    def write(self, reference):
        self.reference = reference
        self._write_properties()

    def _read_xml_attributes(self):
        self.element_id = self.lxml_element.get("xmi.id")

        nodes = []
        nodes.append((self.lxml_element,))

        if self._get_tag(self.lxml_element) == "Association":
            nodes.append(self.lxml_element.xpath("UML:Association.connection/UML:AssociationEnd", namespaces=self.xpath[1]))

        for attr_name in Connector.SOURCE:
            s_id = nodes[len(nodes) - 1][0].get(attr_name)
            if s_id:
                self.source_id = s_id
                break

        for attr_name in Connector.DESTINATION:
            d_id = nodes[len(nodes) - 1][len(nodes) - 1].get(attr_name)
            if d_id:
                self.dest_id = d_id
                break

        for a in Connector.ATRIBUTES:
                try:
                    if isinstance(a[0], tuple) and len(nodes) == 2:
                        n = 2
                    elif not isinstance(a[0], tuple) and len(nodes) == 1:
                        n = 1
                    elif not isinstance(a[0], tuple) and len(nodes) == 2:
                        n = 1
                    else:
                        continue

                    for f in range(n):
                        attribute_value = nodes[n - 1][f].get(a[1])

                        if attribute_value:
                            if len(a) == 2:
                                value = attribute_value
                            elif len(a) == 3 and callable(a[2]):
                                value = a[2](attribute_value)
                            elif len(a) == 3 and not callable(a[2]):
                                value = a[2][attribute_value]

                            if n == 2:
                                self.values[a[0][f]] = value
                            elif n == 1:
                                self.values[a[0]] = value
                except KeyError:
                    print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                    continue

    def _read_tagged_values(self):
        for a in Connector.TAGGED_VALUES:
            try:
                tag_value = self.lxml_element.xpath(
                    "UML:ModelElement.taggedValue/UML:TaggedValue[@tag='" + a[1] + "']/@value",
                    namespaces=self.xpath[1]) or \
                    self.lxml_element.xpath(
                        "//UML:TaggedValue[@tag='" + a[1] + "'][@modelElement='" + self.element_id + "']/@value",
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
        nodes = []
        nodes.append((self.lxml_element,))

        if self._get_tag(self.lxml_element) == "Association":
            nodes.append(self.lxml_element.xpath("UML:Association.connection/UML:AssociationEnd", namespaces=self.xpath[1]))

        for a in Connector.CHILDREN_NODES:
            try:
                if isinstance(a[0], tuple) and len(nodes) == 2:
                    n = 2
                elif not isinstance(a[0], tuple) and len(nodes) == 1:
                    n = 1
                elif not isinstance(a[0], tuple) and len(nodes) == 2:
                    n = 1
                else:
                    continue

                for f in range(n):
                    node_value = nodes[n - 1][f].xpath(a[1], namespaces=self.xpath[1])

                    if node_value:
                        if isinstance(node_value, list):
                            node_value = node_value[0]

                        if len(a) == 2:
                            value = node_value
                        elif len(a) == 3 and callable(a[2]):
                            value = a[2](node_value)
                        elif len(a) == 3 and not callable(a[2]):
                            value = a[2][node_value]

                        if n == 2:
                            self.values[a[0][f]] = value
                        elif n == 1:
                            self.values[a[0]] = value
            except KeyError:
                print "Value " + str(value) + " for: " + a[0] + " is not supported!"
                continue

    def _read_direction(self):
        direction = "Unspecified"
        if self.type == "Association":
            nodes = (self.lxml_element.xpath("UML:Association.connection/UML:AssociationEnd", namespaces=self.xpath[1]))

            transform = {
                "true": True,
                "false": False
            }

            d1 = transform[nodes[0].get("isNavigable")]
            d2 = transform[nodes[1].get("isNavigable")]

            if not d1 and d2:
                direction = "Source to Destination"
            elif d1 and not d2:
                direction = "Destination to Source"
            elif d1 and d2:
                direction = "Bidirectional"

        self.values["direction"] = direction

    def _write_properties(self):
        for a in self.values:
            try:
                self.reference.values[a] = (self.values[a] or '')
            except Exception as e:
                if "Invalid attribute" in e.message:
                    print "Connector type: " + self.type + " not suppoort attribute " + str(a)
                    continue

    def _get_tag(self, element):
        tag = element.tag
        if '}' in tag:
            ns, local = tag.split('}', 1)
            return local
        else:
            return tag
