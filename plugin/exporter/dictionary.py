#coding=utf-8
__author__ = 'Michal Petrovič'


class Dictionary:

    DIAGRAM_TYPE = {
        "UseCaseDiagram": "Use Case diagram",
        "ObjectDiagram": "Object diagram",
        "ClassDiagram": "Class diagram",
        "ActivityDiagram": "Activity diagram",
        "StateDiagram": "State diagram"
    }

    ELEMENT_TYPE = {
        "StartState": ("Pseudostate", "initial"),
        "EndState": "FinalState",
        "Decision": ("Pseudostate", "branch"),
        "Package": "Package",
        "Object": "Object",
        "UseCase": "UseCase",
        "Actor": "Actor",
        "Class": "Class",
        "Note": "Comment",
        #None: "Merge",
        "State": "SimpleState",
        #None: "VerticalSynchronization",
        "HorizontalSynchronization": ("Pseudostate", "join"),
        # ("Pseudostate", "fork"): "HorizontalSynchronization",
        "Activity": "ActionState",
        "Interface": "Interface",
        "Boundary": "Boundary"
    }

    CONNECTION_TYPE = {
        #"Note Link": None,
        "Implementation": "Abstraction",
        "Generalization": "Generalization",
        "Dependency": "Dependency",
        "Control Flow": ("Transition", "ActivityGraph"),
        "StateTransition": ("Transition", "StateMachine"),
        "Include": "Include",
        "Extend": "Extend",
        "AssociationUseCase": "Association",
        "AssociationInstance": "Association",
        "Association": "Association",
        "Agregation": ("Association", "aggregate"),
        "Compose": ("Association", "composite")
    }