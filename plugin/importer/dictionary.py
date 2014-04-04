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
        ("Pseudostate", "vjoin"): "VerticalSynchronization",
        ("Pseudostate", "join"): "HorizontalSynchronization",
        ("Pseudostate", "fork"): "HorizontalSynchronization",
        "ActionState": "Activity",
        "Interface": "Interface",
        "Boundary": "Boundary"
    }

    CONNECTION_TYPE = {
        "NoteLink": "Note Link",
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