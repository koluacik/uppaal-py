"""The definition of Transition class resides here."""

import lxml.etree as ET

from .simplethings import Constraint, Label


class Transition:
    """Class for edges of the TA.

    Many of the attributes are optional. Non existent ones are simply stored as
    None.

    Attributes:
        source: String of the form "idX". References locations or branchpoints.
        target: String of the form "idX". References locations or branchpoints.
        select: Label object with kind 'select'. See UPPAAL documentation.
        guard: Constraint object with kind 'guard'. See UPPAAL documentation.
        synchronisation: Label object with kind 'synchronisation'.
            See UPPAAL documentation.
        assignment: Label object with kind 'assignment'. See UPPAAL
            documentation.
        testcode: Label object with kind 'testcode'. See UPPAAL documentation.
        probability: Label object with kind 'probability'. See UPPAAL
            documentation.
        comments: Label object with kind 'comments'. See UPPAAL
            documentation.
        nails: List of Nail objects.
    """

    def __init__(self, **kwargs):
        """Construct a Transition object from keyword args.

        All arguments except source and target are optional.

        Args:
            source: String, id of the source location.
            target: String, id of the target location.
            select: Label with kind "select". See UPPAAL documentation.
            guard: Constraint object.
            synchronisation: Label with kind "synchronisation".
            testcode: Label with kind "testcode".
            probability: Label with kind "probability".
            comments: Label...
            nails: List of Nail objects.
            template: The parent template. Set by TAGraph.
        """
        self.source = kwargs["source"]
        self.target = kwargs["target"]
        self.select = kwargs.get("select")
        self.guard = kwargs.get("guard")
        self.synchronisation = kwargs.get("synchronisation")
        self.assignment = kwargs.get("assignment")
        self.testcode = kwargs.get("testcode")
        self.probability = kwargs.get("probability")
        self.comments = kwargs.get("comments")
        self.nails = kwargs.get("nails") if kwargs.get("nails") is not None else []
        self.template = None

    @classmethod
    def from_element(cls, et):
        """Construct a Transition from an Element object, and return it."""
        kw = {}
        kw["source"] = et.find("source").get("ref")
        kw["target"] = et.find("target").get("ref")

        for label in et.iter("label"):
            l_kind = label.get("kind")
            label_obj = Label.from_element(label)
            if l_kind == "guard":
                label_obj = Constraint.from_label(label_obj)
            kw[l_kind] = label_obj

        kw["nails"] = [Nail(int(nail.get("x")), int(nail.get("y"))) for nail in et.iter("nail")]

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

    def get_constraints(self):
        """Return a list of simple constraints on this transition."""
        if self.guard is not None:
            return self.guard.constraints
        else:
            return []


class Nail:
    """Class for storing 'nails' on the edges of the TA.

    Attributes:
        pos: Pair of ints.
    """

    def __init__(self, x, y):
        """Construct Nail from an int pair.

        Args:
            x: Int, the x comp. of the position of the Nail.
            y: Int, the y comp. of the position of the Nail.
        """
        self.pos = x, y

    @classmethod
    def from_element(cls, et):
        """Construct Nail from an Element."""
        return cls(int(et.get("x")), int(et.get("y")))

    def to_element(self):
        """Construct an element from Nail object."""
        return ET.Element("nail", attrib={"x": str(self.pos[0]), "y": str(self.pos[1])})
