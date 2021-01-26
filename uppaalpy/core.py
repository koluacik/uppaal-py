"""Core module for processing xml files."""

import lxml.etree as ET
import xml.dom.minidom as dom
import networkx as nx
from uppaalpy import constraint as c

class NTA:
    """UPPAAL system of extended timed automata object.

    Attributes:
        declaration: Declaration object for global declarations.
        templates: List of TA template objects.
        system: Declaration object for template instantiations and system 
            declaration.
        queries: List of query objects.
    """

    def __init__(self, **kwargs):
        """Initializer for TA. 

        Args:
            **kwargs: Keyword arguments for initializing the NTA. See __init__.
        Returns:
            A NTA object.
        """
        self.declaration = kwargs.get('declaration')
        self.templates = kwargs.get('templates') or []
        self.system = kwargs['system']
        self.queries = kwargs['queries']

    @classmethod
    def from_xml(cls, path):
        """Construct NTA from file path, and return it."""
        return NTA.from_element(ET.parse(path).getroot())
    

    @classmethod
    def from_element(cls, et):
        """Construct NTA from Element, and return it."""
        kw = {}
        kw['declaration'] = Declaration.from_element(et.find('declaration'))
        kw['templates'] = [Template.from_element(template) for template in
                et.iterchildren('template')]
        kw['system'] = SystemDeclaration.from_element(et.find('system'))
        if et.find('queries') is None:
            kw['queries'] = []
        else:
            kw['queries'] = [Query.from_element(query) for query in \
                    et.find('queries').iter('query')]
        return cls(**kw)

    def to_element(self):
        """Construct an Element object, and return it."""
        root = ET.Element('nta')

        if self.declaration is not None:
            et_declaration = ET.SubElement(root, 'declaration')
            et_declaration.text = self.declaration.text

        for template in self.templates:
            root.append(template.to_element())

        root.append(self.system.to_element())
        queries = ET.SubElement(root, 'queries')
        for query in self.queries:
            queries.append(query.to_element())

        return root
    
    def to_string(self, pretty=False):
        """Construct a string, and return it.

        If pretty is True, the resulting str will be parsed by
        sml.dom.minidom and converted to str again with toprettyxml method.
        """
        string = ET.tostring(self.to_element(), encoding='unicode')
        if pretty: return dom.parseString(string).toprettyxml()
        else: return string

    def to_file(self, path, pretty=False):
        """Convert the NTA object to a string, and print it to a file.

        Args:
            path: String denoting the path of the output file.
            pretty: Whether to pretty print, see: NTA.to_string.
        """
        (ET.ElementTree(self.to_element())).write(path, encoding='utf-8', pretty_print=pretty)

    def _display(self):
        """Print the object, used for debug purposes."""

        print('NTA:')
        if self.declaration._display() is not None:
            self.declaration._display()
        [template._display() for template in self.templates]
        self.system._display()
        [query._display() for query in self.queries]

class Template:
    """Template for extended timed automaton.

    Attributes:
        name: Name object for storing name of the TA.
        parameter: Parameter object with template parameters.
        declaration: Declaration object with local declarations.
        graph: NetworkX MultiDiGraph object with location and branchpoints
            as nodes and transitions as edges. NetworkX requires nodes and 
            edges to be hashable. For this reason, actual Node and Transition
            objects are 'attached' to the graph nodes and edges as attributes.
        edges: Ordered list of edges for constant time access.
            edges[n] is the n'th edge read from the xml file in the graph.
        locations: Dictionary of named locations for constant time access.
            locations[foo] is the location with name foo. This is only useful
            if all locations are uniquely identified with their name fields.
            Otherwise you must use the id field of locations to identify them.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.parameter = kwargs.get('parameter')
        self.declaration = kwargs.get('declaration')
        self.graph = kwargs.get('graph') or nx.MultiDiGraph()
        self.graph.initial_location = kwargs.get('initial_location')
        self.edges = kwargs['edges']
        self.locations = kwargs['locations']

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Template object. Called from NTA.from_element."""
        kw = {}

        kw['name'] = Name.from_element(et.find('name'))
        kw['parameter'] = Parameter.from_element(et.find('parameter'))
        kw['declaration'] = Declaration.from_element(et.find('declaration'))
        kw['graph'] = nx.MultiDiGraph()
        kw['graph'].counter = 0
        kw['edges'] = []
        kw['locations'] = {}

        t_name = kw['name'].name

        for l in et.iter('location'):
            loc = Location.from_element(l) 
            kw['graph'].add_node((t_name, loc.id), obj = loc)
            if (loc.name != None):
                kw['locations'][loc.name.name] = loc

        for b in et.iter('branchpoint'):
            bp = Location.from_element(l) 
            kw['graph'].add_node((t_name, bp.id), obj = bp)

        kw['initial_location'] = (t_name, et.find('init').get('ref'))

        for t in et.iter('transition'):
            trans = Transition.from_element(t)
            add_edge_wrapper(kw['graph'], t_name, trans)
            kw['edges'].append(trans)

        return cls(**kw)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element('template')
        element.append(self.name.to_element())
        if self.parameter is not None:
            element.append(self.parameter.to_element())
        if self.declaration is not None:
            element.append(self.declaration.to_element())
        element.extend(self._graph_to_element())
        return element

    def get_nodes(self):
        """Return a list of nodes from the multidigraph."""
        return [data['obj'] for node, data in self.graph.nodes(data = True)]

    def get_edges(self):
        """Return a list of transitions from the multidigraph."""
        edges = sorted(self.graph.edges(data = True),
                key = lambda x: x[2]['obj'].edge_id)
        return [data['obj'] for source, target, data in edges]

    def get_initial_location(self):
        return self.graph.initial_location


    def _graph_to_element(self):
        """Convert the multidigraph to an Element. Called from Template.to_element."""
        elements = [node.to_element() for node in self.get_nodes()]
        initial = self.get_initial_location();
        elements.append(ET.Element('init', attrib = {'ref': initial[1]}))
        elements.extend([edge.to_element() for edge in self.get_edges()])
        return elements

    def _display(self):
        """Print the object, used for debug purposes."""
        print('TEMPLATE:')
        self.name._display()
        print()
        if (self.parameter is not None):
            self.parameter._display()
            print()
        if (self.declaration is not None):
            self.declaration._display()
            print()
        [node[1]['obj']._display() for node in self.graph.nodes(data = True)]
        print('INIT:', self.graph.initial_location)
        print()
        [edge[2]['obj']._display() for edge in 
                sorted(self.graph.edges(data = True),
                    key = lambda x: x[2]['obj'].edge_id)]

class Node:
    """Abstract class for nodes of the multidigraph in TA templates.

    This class is extended by BranchPoint and Location classes.

    Attributes:
        id: String of the form "idX".
        pos: Pair of ints for storing the position of the node.
    """

    tag = ""

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.pos = kwargs['pos']

    @classmethod
    def from_element(cls, et):
        """Construct a Node from an Element object, and return it.

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

        return cls(**kw)

    def to_element(self):
        """Convert this object to an Element. Is extended by Location.to_element."""
        element = ET.Element(self.tag, attrib =
                {'id': self.id, 'x': str(self.pos[0]), 'y': str(self.pos[1])})
        return element

    def _display(self):
        """Print the object, used for debug purposes."""
        print(self.tag, ': ', self.id, ' -> ', self.pos, sep='')

class BranchPoint(Node):
    """Derived class of Node.

    The only extension is the added class attribute tag.
    """

    tag = 'branchpoint'

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
        super().__init__(**kwargs)
        self.name = kwargs.get('name')
        self.invariant = kwargs.get('invariant')
        self.exponentialrate = kwargs.get('exponentialrate')
        self.testcodeEnter = kwargs.get('testcodeEnter')
        self.testcodeExit = kwargs.get('testcodeExit')
        self.comments = kwargs.get('comments')
        self.committed = kwargs.get('is_committed') or False
        self.urgent = kwargs.get('is_urgent') or False

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
            element.append(self.exponentialrat.to_element())
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
    
    def _display(self):
        """Print the object, used for debug purposes."""
        super()._display()
        if (self.name is not None):
            self.name._display()
        if (self.invariant is not None):
            self.invariant._display()
        if (self.exponentialrate is not None):
            self.exponentialrate._display()
        if (self.testcodeEnter is not None):
            self.testcodeEnter._display()
        if (self.testcodeExit is not None):
            self.testcodeExit._display()
        if (self.comments is not None):
            self.comments._display()
        print('committed: ', self.committed, ' urgent: ', self.urgent, sep='')
        print()

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

    def _display(self):
        """Print the object, used for debug purposes."""
        print('TRANSITION from', self.source, 'to', self.target)
        if (self.select is not None):
            self.select._display()
        if (self.guard is not None):
            self.guard._display()
        if (self.synchronisation is not None):
            self.synchronisation._display()
        if (self.assignment is not None):
            self.assignment._display()
        if (self.testcode is not None):
            self.testcode._display()
        if (self.probability is not None):
            self.probability._display()
        if (self.comments is not None):
            self.comments._display()
        [nail._display() for nail in self.nails]
        print()

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

    def _display(self):
        """Print the object, used for debug purposes."""
        print('NAIL:', self.pos)


class Label:
    """A label object from UPPAAL. 

    Many location and edge attributes in UPPAAL are stored as xml elements with
    tag 'label', and differentiated by their attribute 'kind'.  The 'content'
    of these elements are currently stored as strings. Finally, they also have
    a location 'x' and 'y'. Some label kinds like test code are not visible in
    the UPPAAL template editor. These labels do not have a pos.

    See subclass Constraint.

    Attributes:
        kind: String for differentiating the kind of the label.
        value: String for storing the content of the label.
        pos: A pair of ints for position. Some label kinds do not have a pos.
    """

    def __init__(self, kind, value, pos=None):
        self.kind = kind
        self.value = value
        self.pos = pos

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Label object. Called from NTA.from_element."""
        pos = (int(et.get('x')), int(et.get('y'))) if et.get('x') is not None else None
        return cls(et.get('kind'), et.text, pos)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element('label', attrib = {'kind': self.kind})
        element.text = self.value
        if self.pos is not None:
            element.set('x', str(self.pos[0]))
            element.set('y', str(self.pos[1]))
        return element

    def _display(self):
        """Print the object, used for debug purposes."""
        print('LABEL kind: ', self.kind, ' value: ', self.value, end = '') 
        if self.pos is not None:
            print(' position: ', self.pos)

class Constraint(Label):
    """A specific label for invariants or transitions in timed automata.

    The attribute 'parsed' simplifies computations involving constraints.
    """

    def __init__(self, obj):
        super().__init__(obj.kind, obj.value, obj.pos)
        self.parsed = c.string_to_simple(self.value)

class SimpleField:
    """Simple text field with fromEt and to_element methods. 

    This class can be thought of as a abstract class for strings with no 
    extra information in UPPAAL. It is a base class for other classes 
    SystemDeclaration, Declaration, and Parameter. They only differ by their
    class attribute tag. This way we can easily serialize different types of
    text fields to xml.
    """
    
    tag = ""

    def __init__(self, text):
        self.text = text

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a SimpleField object. Called from NTA.from_element."""
        return cls(et.text) if et is not None else None

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element

        This method is meant to be used by derived classes.
        """

        element = ET.Element(self.tag)
        element.text = self.text
        return element

    def _display(self):
        """Print the object, used for debug purposes."""
        print(self.tag, ': ', self.text[:20], sep = '')

class SystemDeclaration(SimpleField):
    """A derived class for simple strings in UPPAAL.

    See base class SimpleField.
    """

    tag = 'system'
        
class Declaration(SimpleField):
    """A derived class for simple strings in UPPAAL.

    See base class SimpleField.
    """

    tag = 'declaration'

class Parameter(SimpleField):
    """A derived class for simple strings in UPPAAL.  
    See base class SimpleField.
    """

    tag = 'parameter'

class Name:
    """An object for Name elements in UPPAAL xml files.

    This class is almost identical to the Label class minus the kind attribute.
    'pos' is meaningless for Name attribute of Templates, but we follow the 
    UPPAAAL xml format regardless.
    """
    
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Name object. Called from NTA.from_element."""
        return cls(et.text, (et.get('x'), et.get('y'))) if et is not None else None

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element('name', attrib = {'x': str(self.pos[0]), 'y': str(self.pos[1])})
        element.text = self.name
        return element

    def _display(self):
        """Print the object, used for debug purposes."""
        print('NAME: ', self.name, int(self.pos[0]), int(self.pos[1]))

class Query:
    """Query object with formula and a comment.

    Attributes:
        formula: String for expression that the NTA will be tested against.
        comment: String for commenting the query.
    """

    def __init__(self, formula, comment):
        """Query object initializer."""
        self.formula = formula
        self.comment = comment

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Query object. Called from NTA.from_element."""
        return cls(et.find('formula').text, et.find('comment').text)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        query = ET.Element('query')
        formula = ET.SubElement(query, 'formula')
        formula.text = self.formula
        comment = ET.SubElement(query, 'comment')
        comment.text = self.comment
        return query

    def _display(self):
        """Print the object, used for debug purposes."""
        print('QUERY:')
        print(self.formula)
        print(self.comment)

def add_edge_wrapper(graph, template_name, edge):
    """Given a graph, template name and an edge, insert the edge into the graph.

    This is a wrapper for the graph.add_edge() method that increments
    the counter attribute of the graph by one. If the edge_id of edge to
    be added is -1 it will be set to counter.
    """
    if edge.edge_id == -1:
        edge.edge_id = graph.counter
    graph.add_edge((template_name, edge.source), (template_name, edge.target),
            obj = edge)
    graph.counter += 1
