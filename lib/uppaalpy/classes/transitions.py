from .simplethings import *

class Transition:
    """Class for edges of the TA.

    Many of the attributes are optional. Non existent ones are simply stored as
    None.

    Attributes:
        source: String of the form "idX". References locations or branchpoints.
        target: String of the form "idX". References locations or branchpoints.
        select: Label object with kind 'select'. See UPPAAL documentation.
        guard: Label object with kind 'guard'. See UPPAAL documentation.
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
        edge_id: Not relevant to UPPAAL. Unlike locations and
            branchpoints, edges in UPPAAL are not uniquely identified by a
            certain attribute. For this reason we enumerate them while iterating
            over the Element object to preserve the order of the edges in the file
            and also to be able to differentiate them in case there exists more
            than two edges from a location to another node in the file. The
            default value of this attribute is -1.
    """

    def __init__(self, **kwargs):
        self.source = kwargs['source']
        self.target = kwargs['target']
        self.select = kwargs.get('select')
        self.guard = kwargs.get('guard')
        self.synchronisation = kwargs.get('synchronisation')
        self.assignment = kwargs.get('assignment')
        self.testcode = kwargs.get('testcode')
        self.probability = kwargs.get('probability')
        self.comments = kwargs.get('comments')
        self.nails = kwargs.get('nails') if kwargs.get('nails') is not None else []
        self.edge_id = -1

    @classmethod
    def from_element(cls, et):
        """Construct a Transition from an Element object, and return it."""
        kw = {}
        kw['source'] = et.find('source').get('ref')
        kw['target'] = et.find('target').get('ref')

        for label in et.iter('label'):
            l_kind = label.get('kind')
            label_obj = Label.from_element(label)
            if l_kind == 'guard':
                label_obj = Constraint(label_obj)
            kw[l_kind] = label_obj

        kw['nails'] = [Nail((nail.get('x'), nail.get('y'))) for nail in
                et.iter('nail')]

        return cls(**kw)

    def to_element(self):
        """Convert this object to an Element. Is extended by Location.to_element."""
        element = ET.Element('transition')
        element.append(ET.Element('source', attrib = {'ref': self.source}))
        element.append(ET.Element('target', attrib = {'ref': self.target}))
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

    def __init__(self, pos):
        self.pos = pos

    @classmethod
    def from_element(cls, et):
        return cls((int(et.get('x')), int(et.get('y'))))

    def to_element(self):
        return ET.Element('nail', attrib = {'x': str(self.pos[0]), 'y': str(self.pos[1])})
