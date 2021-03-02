import networkx as nx
from itertools import count
import lxml.etree as ET

class TAGraph(nx.MultiDiGraph):
    """Derived class of NetworkX MultiDiGraph.

    Do not use typical networkx methods to modify the graph.
    Extends the base class with following attributes.

    Extra attributes:
        initial_location: String for initial location ref. (ex: "id0")
        named_locations: Dictionary for mapping from location names to locations.
        transitions: List of transitions, in the order read from file.
        template_name: String for name of the template.
        transition_counter: Iterator for uniquely assigning a uniquely determined
            key to each transition in the MultiDiGraph.
    """

    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.initial_location = ""
        self._named_locations = {}
        self._transitions = []
        self.template_name = ""
        self._transition_counter = count()

    def add_location(self, loc):
        """Insert a Location object.

        Only named Locations can be used for path analysis. Named Locations
        are also registered in self._named_locations.

        """
        self.add_node((self.template_name, loc.id), obj=loc)
        if (loc.name != None):
            self._named_locations[loc.name.name] = loc

    def add_branchpoint(self, bp):
        """Insert a BranchPoint object. See add_location()."""
        self.add_node((self.template_name, bp.id), obj=bp)

    def add_transition(self, trans):
        """Insert a Transition object.

        self._transition_counter is used for manually assigning a unique
        key to the edge. Also, self._transitions is used for linear time
        serializations and constant time lookups.
        """
        self.add_edge(
                (self.template_name, trans.source),
                (self.template_name, trans.target),
                obj=trans,
                key=next(self._transition_counter))
        self._transitions.append(trans)

    def to_element(self):
        """Convert the multidigraph to an Element."""
        elements = [data['obj'].to_element() for _, data in \
                list(self.nodes(data=True))]
        elements.append(ET.Element('init', \
                attrib={'ref': self.initial_location}))
        elements.extend([t.to_element() for t in self._transitions])
        return elements
