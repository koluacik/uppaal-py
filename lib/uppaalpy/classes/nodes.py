from .simplethings import *

class Node:
    """Abstract class for nodes of the multidigraph in TA templates.

    This class is extended by BranchPoint and Location classes.

    Attributes:
        id: String of the form "idX".
        pos: Pair of ints for storing the position of the node.
    """

    tag = None
    id = None
    pos = None

    @staticmethod
    def generate_dict(et):
        """Construct a dict from an Element object, and return it.

        Notice that only 'id' and 'pos' are relevant for BranchPoints. Other
        attributes are not present in the XML file and gracefully ignored for
        BranchPoint objects.
        """
        kw = {}
        kw['id'] = et.get('id')
        kw['pos'] = int(et.get('x')), int(et.get('y'))
        kw['name'] = Name.from_element(et.find('name'))

        for label in et.iter('label'):
            l_kind = label.get('kind')
            label_obj = Label.from_element(label)

            if l_kind == 'invariant':
                label_obj = Constraint(label_obj)

            kw[l_kind] = label_obj

        kw['committed'] = et.find('committed') in et
        kw['urgent'] = et.find('urgent') in et

        return kw

    def to_element(self):
        """Convert this object to an Element. Is extended by Location.to_element."""
        element = ET.Element(self.tag, attrib=
                {'id': self.id, 'x': str(self.pos[0]), 'y': str(self.pos[1])})
        return element

class BranchPoint(Node):
    """Derived class of Node.

    The only extension is the added class attribute tag.
    """

    tag = 'branchpoint'


    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.pos = kwargs['pos']

    @classmethod
    def from_element(cls, et):
        """Generate a dictionary for initialization from et and construct a BP.
        """
        return cls(**super().generate_dict(et))

class Location(Node):
    """Derived class of Node.

    This class has additional labels and text fields that are not present in
    BranchPoint objects. Refer to the UPPAAL documentation for information
    on different label kinds. This class does not extend Node.from_element since
    the method of the superclass already captures all the required information
    about the location.

    Attributes:
        name: Name object.
        invariant: Label object for location invariants.
        exponentialrate: Label object. See UPPAAL documentation.
        testcodeEnter: Label object. See UPPAAL documentation.
        testcodeExit: Label object. See UPPAAL documentation.
        comments: Label object for storing comments.
        committed: Boolean value for whether the location is committed.
        urgent: Boolean value for whether the location is urgent.
    """

    tag = 'location'

    def __init__(self, **kwargs):
        """Construct a Node from an Element object, and return it.

        This method extends Node.__init__.
        """
        self.id = kwargs['id']
        self.pos = kwargs['pos']
        self.name = kwargs.get('name')
        self.invariant = kwargs.get('invariant')
        self.exponentialrate = kwargs.get('exponentialrate')
        self.testcodeEnter = kwargs.get('testcodeEnter')
        self.testcodeExit = kwargs.get('testcodeExit')
        self.comments = kwargs.get('comments')
        self.committed = kwargs.get('is_committed') or False
        self.urgent = kwargs.get('is_urgent') or False

    @classmethod
    def from_element(cls, et):
        """Generate a dictionary for initialization from et and construct a Loc.
        """
        return cls(**super().generate_dict(et))

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
            element.append(ET.Element('committed'))
        if self.urgent:
            element.append(ET.Element('urgent'))
        return element

    def get_constraints(self):
        """Return a list of simple constraints on this location."""
        if self.invariant is not None:
            return self.invariant.constraints
        else:
            return []
