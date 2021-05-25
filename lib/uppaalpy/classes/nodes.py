"""Module for definitions of abstract class Node, and subclasses BranchPoint and Location."""

from typing import Any, Dict, List, Optional, Tuple, Type

import lxml.etree as ET

from uppaalpy.classes import templates as t
from uppaalpy.classes.context import Context
from uppaalpy.classes.expr import ConstraintExpression
from uppaalpy.classes.simplethings import ConstraintLabel, Label, Name


class Node:
    """Abstract class for nodes of the multidigraph in TA templates.

    This class is extended by BranchPoint and Location classes.

    Attributes:
        id: String of the form "idX".
        pos: Pair of ints for storing the position of the node.
    """

    tag = None  # type: Optional[str]
    id = "null"  # type: str
    pos = (0, 0)  # type: Tuple[int, int]

    @staticmethod
    def generate_dict(et, ctx: Context) -> Dict[str, Any]:
        """Construct a dict from an Element object, and return it.

        Notice that only 'id' and 'pos' are relevant for BranchPoints. Other
        attributes are not present in the XML file and ignored for BranchPoint
        objects.
        """
        kw = {}  # type: Dict[str, Any]
        kw["id"] = et.get("id")
        kw["pos"] = int(et.get("x")), int(et.get("y"))
        kw["name"] = Name.from_element(et.find("name"))

        for label in et.iter("label"):
            l_kind = label.get("kind")
            label_obj = Label.from_element(label)

            if l_kind == "invariant":
                label_obj = ConstraintLabel.from_label(label_obj, ctx)

            kw[l_kind] = label_obj

        kw["committed"] = et.find("committed") in et
        kw["urgent"] = et.find("urgent") in et

        return kw

    def to_element(self):
        """Convert this object to an Element. Is extended by Location.to_element."""
        element = ET.Element(
            self.tag,
            attrib={"id": self.id, "x": str(self.pos[0]), "y": str(self.pos[1])},
        )
        return element


class BranchPoint(Node):
    """Derived class of Node.

    The only extension is the added class attribute tag.
    """

    tag = "branchpoint"

    def __init__(self, **kwargs):
        """Accept id string and position pair, and generate a Branchpoint."""
        self.id = kwargs["id"]
        self.pos = kwargs["pos"]

    @classmethod
    def from_element(cls: Type["BranchPoint"], et, ctx: Context) -> "BranchPoint":
        """Generate a dictionary for initialization from et and construct a BP."""
        return cls(**super().generate_dict(et, ctx))


class Location(Node):
    """Derived class of Node.

    This class has additional labels and text fields that are not present in
    BranchPoint objects. Refer to the UPPAAL documentation for information
    on different label kinds.

    Attributes:
        id: id string.
        pos: Int pair.
        name: Name object.
        invariant: ConstraintLabel object for location invariants.
        exponentialrate: Label object. See UPPAAL documentation.
        testcodeEnter: Label object. See UPPAAL documentation.
        testcodeExit: Label object. See UPPAAL documentation.
        comments: Label object for storing comments.
        committed: Boolean value for whether the location is committed.
        urgent: Boolean value for whether the location is urgent.
        template: The parent template, set by TAGraph.
    """

    tag = "location"

    def __init__(self, **kwargs) -> None:
        """Construct a Node from an Element object, and return it.

        This method extends Node.__init__.
        """
        self.id = kwargs["id"]
        self.pos = kwargs["pos"]
        self.name = kwargs.get("name")  # type: Optional[Name]
        self.invariant = kwargs.get("invariant")  # type: Optional[ConstraintLabel]
        self.exponentialrate = kwargs.get("exponentialrate")  # type: Optional[Label]
        self.testcodeEnter = kwargs.get("testcodeEnter")  # type: Optional[Label]
        self.testcodeExit = kwargs.get("testcodeExit")  # type: Optional[Label]
        self.comments = kwargs.get("comments")  # type: Optional[Label]
        self.committed = kwargs.get("committed") or False  # type: bool
        self.urgent = kwargs.get("urgent") or False  # type: bool
        self.template = None  # type: Optional[t.Template]

    @classmethod
    def from_element(cls: Type["Location"], et, ctx: Context) -> "Location":
        """Generate a dictionary for initialization from et and construct a Loc."""
        return cls(**super().generate_dict(et, ctx))

    def to_element(self):
        """Convert this object to an Element.

        This method extends Node.to_element.
        """
        element = super().to_element()
        if self.name is not None:
            element.append(self.name.to_element())
        if self.invariant is not None:
            element.append(self.invariant.to_element())
        if self.exponentialrate is not None:
            element.append(self.exponentialrate.to_element())
        if self.testcodeEnter is not None:
            element.append(self.testcodeEnter.to_element())
        if self.testcodeExit is not None:
            element.append(self.testcodeExit.to_element())
        if self.comments is not None:
            element.append(self.comments.to_element())
        if self.committed:
            element.append(ET.Element("committed"))
        if self.urgent:
            element.append(ET.Element("urgent"))
        return element

    def get_constraints(self) -> List[ConstraintExpression]:
        """Return a list of constraints on this location."""
        if self.invariant is not None:
            return self.invariant.constraints
        else:
            return []

    def get_constraint_label(self) -> Optional[ConstraintLabel]:
        """Return the invariant label."""
        return self.invariant

    def create_constraint_label(self, exp: ConstraintExpression, ctx: Context):
        """Create invariant label."""
        self.invariant = ConstraintLabel("invariant", "", self.pos, ctx, [exp])

    def remove_constraint_label(self) -> None:
        """Remove invariant."""
        self.invariant = None
