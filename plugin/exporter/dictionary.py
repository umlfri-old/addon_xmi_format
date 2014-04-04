#coding=utf-8
__author__ = 'Michal Petrovič'


class Dictionary:

    DIAGRAM_TYPE = {
        "Use Case diagram": "UseCaseDiagram",
        "Object diagram": "ObjectDiagram",
        "Class diagram": "ClassDiagram",
        "Activity diagram": "ActivityDiagram",
        "State diagram": "StateDiagram"
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
        "Merge": ("Pseudostate", "branch"),
        "State": "SimpleState",
        "VerticalSynchronization": ("Pseudostate", "vjoin"),
        #"VerticalSynchronization": ("Pseudostate", "vfork"),
        "HorizontalSynchronization": ("Pseudostate", "join"),
        #"HorizontalSynchronization": ("Pseudostate", "fork"),
        "Activity": "ActionState",
        "Interface": "Interface",
        "Boundary": "Boundary"
    }

    CONNECTION_TYPE = {
        "Note Link": "NoteLink",
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