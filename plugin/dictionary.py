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
        ("Pseudostate", "initial"): "StartState",
        "FinalState": "EndState",
        ("Pseudostate", "branch"): "Decision",
        "Package": "Package",
        "Object": "Object",
        "UseCase": "UseCase",
        "Actor": "Actor",
        "Class": "Class",
        "Comment": "Note",
        #None: "Merge",
        "SimpleState": "State",
        #None: "VerticalSynchronization",
        ("Pseudostate", "join"): "HorizontalSynchronization",
        ("Pseudostate", "fork"): "HorizontalSynchronization",
        "ActionState": "Activity",
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