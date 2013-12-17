#coding=utf-8
__author__ = 'Michal Petrovič'


class Dictionary:

    DIAGRAM_TYPE = {
        #None: "Use Case diagram",
        #None: "Object diagram",
        #None: "Class diagram",
        #None: "Activity diagram",
        #None: "State diagram"
    }

    ELEMENT_TYPE = {
        #None: "StartState",
        #None: "EndState",
        #None: "Decision",
        "Package": "Package",
        #None: "Object",
        #None: "UseCase",
        #None: "Actor",
        "Class": "Class",
        #None: "Note",
        #None: "Merge",
        #None: "State",
        #None: "VerticalSynchronization",
        #None: "HorizontalSynchronization",
        #None: "Activity",
        "Interface": "Interface"
        #None: "Boundary"
    }

    CONNECTION_TYPE = {
        #None:"Note Link",
        #None:"Implementation",
        #None:"Generalization",
        #None:"Dependency",
        #None:"Control Flow",
        #None:"StateTransition",
        #None:"Include",
        #None:"Extend",
        #None:"AssociationUseCase",
        #None:"AssociationInstance",
        #None:"Association",
        #None:"Agregation",
        #None:"Compose"
    }