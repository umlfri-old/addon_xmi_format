#coding=utf-8
__author__ = 'Michal Petrovič'

from lxml import etree


class Connector:

    ATRIBUTES = (
        ("name", "name"),
        (("SRole", "DRole"), "name"),
        (("SCardinality", "DCardinality"), "multiplicity")
    )

    TAGGED_VALUES = (
        ("note", "documentation"),
    )

    CHILDREN_NODES = (
        ("stereotype", "ModelElement.stereotype/Stereotype/@name"),
        ("guard", "Transition.guard/Guard/Guard.expression/BooleanExpression/@body"),
    )

    SOURCE_TO_DESTINATION = {
        "Dependency": ("client", "supplier"),
        "Generalization": ("subtype", "supertype"),
        "Implementation": ("subtype", "supertype"),
        "Include": ("base", "addition"),
        "Extend": ("extension", "base"),
        "AssociationUseCase": ("type", "type"),
        "AssociationInstance": ("type", "type"),
        "Association": ("type", "type"),
        "Agregation": ("type", "type"),
        "Compose": ("type", "type"),
        "Control Flow": ("source", "target"),
        "StateTransition": ("source", "target")
    }

    def __init__(self, reference, lxml_element, kind, prefix, exporter):
        self.reference = reference
        self.lxml_element = lxml_element
        self.kind = kind
        self.prefix = prefix
        self.exporter = exporter

        self.element_id = "ID_" + unicode(id(self.reference))
        self.asociation_ends = []

    def write(self):
        self._write_association_ends()
        self._write_xml_attributes()
        self._write_tagged_values()
        self._write_children_nodes()
        self._write_direction()

    def _write_association_ends(self):
        if self.reference.type.name in ("AssociationUseCase", "AssociationInstance", "Association", "Agregation", "Compose"):
            wrap_node = etree.SubElement(self.lxml_element, self.prefix + "Association.connection")
            for _ in range(2):
                self.asociation_ends.append(etree.SubElement(wrap_node, self.prefix + "AssociationEnd", association=self.element_id))

            self.asociation_ends[0].set("aggregation", "none")
            self.asociation_ends[1].set("aggregation", self.kind or "none")

    def _write_xml_attributes(self):
        self.lxml_element.set("xmi.id", self.element_id)
        self.lxml_element.set("namespace", self.lxml_element.xpath("(ancestor::*/@xmi.id)[last()]", namespaces=self.lxml_element.nsmap)[0])

        if self.asociation_ends:
            nodes = (self.asociation_ends[0], self.asociation_ends[1])
        else:
            nodes = (self.lxml_element,) * 2

        names = Connector.SOURCE_TO_DESTINATION[self.reference.type.name]
        values = ("ID_" + unicode(id(self.reference.source)), "ID_" + unicode(id(self.reference.destination)))

        for n in range(2):
            nodes[n].set(names[n], values[n])

        for a in Connector.ATRIBUTES:
            try:
                if isinstance(a[0], tuple):
                    n = 2
                else:
                    n = 1

                for f in range(n):
                    if n == 2:
                        attribute_value = dict(self.reference.all_values)[a[0][f]]
                    else:
                        attribute_value = dict(self.reference.all_values)[a[0]]

                    if attribute_value:
                        if len(a) == 2:
                            value = attribute_value
                        elif len(a) == 3 and callable(a[2]):
                            value = a[2](attribute_value)
                        elif len(a) == 3 and not callable(a[2]):
                            value = a[2][attribute_value]

                        if n == 2:
                            self.asociation_ends[f].set(a[1], value)
                        else:
                            self.lxml_element.set(a[1], value)
            except KeyError:
                print "Connection " + self.reference.type.name + " does not support " + unicode(a[0]) + " attribute!"
                continue

    def _write_tagged_values(self):
        wrap_node = None
        for a in Connector.TAGGED_VALUES:
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

    def _write_children_nodes(self):
        for a in Connector.CHILDREN_NODES:
            try:
                if isinstance(a[0], tuple):
                    n = 2
                else:
                    n = 1

                for f in range(n):
                    if n == 2:
                        attribute_value = dict(self.reference.all_values)[a[0][f]]
                    else:
                        attribute_value = dict(self.reference.all_values)[a[0]]

                    if attribute_value:
                        if len(a) == 2:
                            value = attribute_value
                        elif len(a) == 3 and callable(a[2]):
                            value = a[2](attribute_value)
                        elif len(a) == 3 and not callable(a[2]):
                            value = a[2][attribute_value]

                        if n == 2:
                            wrap_node = self.asociation_ends[f]
                        else:
                            wrap_node = self.lxml_element

                        path_nodes = a[1].split('/')
                        for path_node in path_nodes:
                            if path_node[0] != '@':
                                wrap_node = etree.SubElement(wrap_node, self.prefix + path_node)
                            else:
                                wrap_node.set(path_node[1:], value)
            except KeyError:
                print "Connection " + self.reference.type.name + " does not support " + unicode(a[0]) + " attribute!"
                continue

    def _write_direction(self):
        if self.asociation_ends:
            direction = dict(self.reference.all_values).get("direction")
            d1 = d2 = False

            if direction == "Source to Destination":
                d1, d2 = False, True
            elif direction == "Destination to Source":
                d1, d2 = True, False
            elif direction == "Bidirectional":
                d1 = d2 = True

            transform = {
                True: "true",
                False: "false"
            }

            self.asociation_ends[0].set("isNavigable", transform[d1])
            self.asociation_ends[1].set("isNavigable", transform[d2])