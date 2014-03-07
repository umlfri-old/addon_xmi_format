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
        #None:"Note Link",
        "Abstraction": "Implementation",
        "Generalization": "Generalization",
        "Dependency": "Dependency",
        ("Transition", "ActivityGraph"): "Control Flow",
        ("Transition", "StateMachine"): "StateTransition",
        "Include": "Include",
        "Extend": "Extend",
        ("Association", "useCase"): "AssociationUseCase",
        #None:"AssociationInstance",
        ("Association", "normal"): "Association",
        ("Association", "aggregate"): "Agregation",
        ("Association", "composite"): "Compose"
    }