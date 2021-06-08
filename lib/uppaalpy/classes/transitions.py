"""The definition of Transition class resides here."""

from typing import List, Optional, Type

import lxml.etree as ET

from uppaalpy.classes import templates as t
from uppaalpy.classes.context import Context
from uppaalpy.classes.expr import ConstraintExpression
from uppaalpy.classes.simplethings import ConstraintLabel, Label, UpdateLabel


class Transition:
    """Class for edges of the TA.

    Many of the attributes are optional. Non existent ones are simply stored as
    None.

    Attributes:
        source: String of the form "idX". References locations or branchpoints.
        target: String of the form "idX". References locations or branchpoints.
        select: Label object with kind 'select'. See UPPAAL documentation.
        guard: ConstraintLabel object with kind 'guard'. See UPPAAL
            documentation.
        synchronisation: Label object with kind 'synchronisation'.
            See UPPAAL documentation.
        assignment: Update Label object with kind 'assignment'. See UPPAAL
            documentation.
        testcode: Label object with kind 'testcode'. See UPPAAL documentation.
        probability: Label object with kind 'probability'. See UPPAAL
            documentation.
        comments: Label object with kind 'comments'. See UPPAAL
            documentation.
        nails: List of Nail objectsAny, .
    """

    def __init__(self, **kwargs) -> None:
        """Construct a Transition object from keyword args.

        All arguments except source and target are optional.

        Args:
            source: String, id of the source location.
            target: String, id of the target location.
            select: Label with kind "select". See UPPAAL documentation.
            guard: ConstraintLabel object.
            synchronisation: Label with kind "synchronisation".
            assignment: UpdateLabel object.
            testcode: Label with kind "testcode".
            probability: Label with kind "probability".
            comments: Label...
            nails: List of Nail objects.
            template: The parent template. Set by TAGraph.
        """
        self.source = kwargs["source"]  # type: str
        self.target = kwargs["target"]  # type: str
        self.select = kwargs.get("select")  # type: Optional[Label]
        self.guard = kwargs.get("guard")  # type: Optional[ConstraintLabel]
        self.synchronisation = kwargs.get("synchronisation")  # type: Optional[Label]
        self.assignment = kwargs.get("assignment")  # type: Optional[UpdateLabel]
        self.testcode = kwargs.get("testcode")  # type: Optional[Label]
        self.probability = kwargs.get("probability")  # type: Optional[Label]
        self.comments = kwargs.get("comments")  # type: Optional[Label]
        self.nails = (
            kwargs.get("nails") if kwargs.get("nails") is not None else []
        )  # type: Optional[List[Nail]]
        self.template: Optional[t.Template] = None  # Optional[Template]

    @classmethod
    def from_element(cls: Type["Transition"], et, ctx: Context) -> "Transition":
        """Construct a Transition from an Element object, and return it."""
        kw = {}
        kw["source"] = et.find("source").get("ref")
        kw["target"] = et.find("target").get("ref")

        for label in et.iter("label"):
            l_kind = label.get("kind")
            label_obj = Label.from_element(label)
            if l_kind == "guard":
                label_obj = ConstraintLabel.from_label(label_obj, ctx)
            elif l_kind == "assignment":
                label_obj = UpdateLabel.from_label(label_obj, ctx)
            kw[l_kind] = label_obj

        kw["nails"] = [
            Nail(int(nail.get("x")), int(nail.get("y"))) for nail in et.iter("nail")
        ]

        return cls(**kw)

    def to_element(self):
        """Convert this object to an Element."""
        element = ET.Element("transition")
        element.append(ET.Element("source", attrib={"ref": self.source}))
        element.append(ET.Element("target", attrib={"ref": self.target}))
        if self.select is not None:
            element.append(self.select.to_element())
        if self.guard is not None:
            element.append(self.guard.to_element())
        if self.synchronisation is not None:
            element.append(self.synchronisation.to_element())
        if self.assignment is not None:
            element.append(self.assignment.to_element())
        if self.testcode is not None:
            element.append(self.testcode.to_element())
        if self.probability is not None:
            element.append(self.probability.to_element())
        if self.comments is not None:
            element.append(self.comments.to_element())
        for nail in self.nails:
            element.append(nail.to_element())
        return element

    def get_constraints(self) -> List[ConstraintExpression]:
        """Return a list of simple constraints on this transition."""
        if self.guard is not None:
            return self.guard.constraints
        else:
            return []

    def get_constraint_label(self) -> Optional[ConstraintLabel]:
        """Return the guard label."""
        return self.guard

    def create_constraint_label(self, exp: ConstraintExpression, ctx: Context) -> None:
        """Create a guard label with the given expression."""
        t = self.template
        t_name = t.name.name
        src, dst = (t_name, self.source), (t_name, self.target)
        slx, sly = t.graph.nodes[src]["obj"].pos
        dlx, dly = t.graph.nodes[dst]["obj"].pos
        guard_pos = (slx + dlx, sly + dly)

        self.guard = ConstraintLabel("guard", "", guard_pos, ctx, [exp])

    def remove_constraint_label(self) -> None:
        """Remove guard."""
        self.guard = None


class Nail:
    """Class for storing 'nails' on the edges of the TA.

    Attributes:
        pos: Pair of ints.
    """

    def __init__(self, x: int, y: int) -> None:
        """Construct Nail from an int pair.

        Args:
            x: Int, the x comp. of the position of the Nail.
            y: Int, the y comp. of the position of the Nail.
        """
        self.pos = x, y

    @classmethod
    def from_element(cls: Type["Nail"], et) -> "Nail":
        """Construct Nail from an Element."""
        return cls(int(et.get("x")), int(et.get("y")))

    def to_element(self):
        """Construct an element from Nail object."""
        return ET.Element("nail", attrib={"x": str(self.pos[0]), "y": str(self.pos[1])})
