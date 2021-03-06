"""Template class definition.

Each template in an NTA represents a Distinct TA recipe.
"""
import lxml.etree as ET

from .nodes import BranchPoint, Location
from .simplethings import Declaration, Name, Parameter
from .tagraph import TAGraph
from .transitions import Transition


class Template:
    """Template for extended timed automaton.

    Attributes:
        name: Name object for storing name of the TA.
        parameter: Parameter object with template parameters.
        declaration: Declaration object with local declarations.
        graph: TAGraph object with location and branchpoints
            as nodes and transitions as edges. Superclass NetworkX MultiDigraphs
            require nodes and edges to be hashable. For this reason, actual Node
            and Transition objects are 'attached' to the graph nodes and edges
            as attributes.
    """

    def __init__(self, **kwargs):
        """Construct a Template."""
        self.name = kwargs.get("name")
        self.parameter = kwargs.get("parameter")
        self.declaration = kwargs.get("declaration")
        self.graph = kwargs.get("graph") or TAGraph()

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Template object. Called from NTA.from_element."""
        kw = {}

        kw["name"] = Name.from_element(et.find("name"))
        kw["parameter"] = Parameter.from_element(et.find("parameter"))
        kw["declaration"] = Declaration.from_element(et.find("declaration"))
        kw["graph"] = TAGraph()

        t_name = kw["name"].name

        kw["graph"].template_name = t_name

        for l in et.iter("location"):
            loc = Location.from_element(l)
            kw["graph"].add_location(loc)

        for b in et.iter("branchpoint"):
            bp = BranchPoint.from_element(b)
            kw["graph"].add_branchpoint(bp)

        kw["graph"].initial_location = et.find("init").get("ref")

        for t in et.iter("transition"):
            trans = Transition.from_element(t)
            kw["graph"].add_transition(trans)

        return cls(**kw)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element("template")
        element.append(self.name.to_element())
        if self.parameter is not None:
            element.append(self.parameter.to_element())
        if self.declaration is not None:
            element.append(self.declaration.to_element())
        element.extend(self.graph.to_element())
        return element
