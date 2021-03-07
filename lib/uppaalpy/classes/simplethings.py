"""Basic classes used by other classes throughout the project."""
import lxml.etree as ET


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
        """Construct a Label object given kind, value, and optional pos.

        For invariants and guards, subclass Constraint is used.

        Args:
            kind: The kind of the label. See example xml files for valid
                strings.
            value: String with the text content of the label.
            pos: Pair of ints denoting the position of the label.
        """
        self.kind = kind
        self.value = value
        self.pos = pos

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Label object."""
        pos = (int(et.get("x")), int(et.get("y"))) if et.get("x") is not None else None
        return cls(et.get("kind"), et.text, pos)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element("label", attrib={"kind": self.kind})
        element.text = self.value
        if self.pos is not None:
            element.set("x", str(self.pos[0]))
            element.set("y", str(self.pos[1]))
        return element


class Constraint(Label):
    """A specific label for invariants or transitions in timed automata.

    The attribute 'parsed' is a list of parsed SimpleConstraint.
    It simplifies computations involving constraints. This class overrides
    the Label.to_element() and Label.from_element() methods. self.value
    is ignored after initialization. Also see class SimpleConstraint.

    Extra Attributes:
        parsed: List of SimpleConstraint.
    """

    def __init__(self, kind, value, pos, constraints=[]):
        """Construct a Constraint from Label args, and optionally, constraints.

        If a non-empty list of constraints is not provided, the value attribute
        is parsed, instead.

        Args:
            kind: String denoting the kind of the constraint. Must be "guard"
                or "invariant".
            value: String denoting the text content of the Label.
            pos: Pair of ints for the position of the Label.
            constraints: List of SimpleConstraint objects. If empty (default),
                value is parsed, instead.
        """
        super().__init__(kind, value, pos)
        self.constraints = (
            constraints
            if constraints
            else SimpleConstraint.parse_inequality(self.value)
        )

    @classmethod
    def from_label(cls, label, constraints=[]):
        """Construct a Constraint from a Label object.

        Args:
            label: A label object.
            constraints: List of SimpleConstraint objects. If empty (default),
                value field of the label is parsed, instead.
        """
        return cls(label.kind, label.value, label.pos, constraints)

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Constraint."""
        pos = (int(et.get("x")), int(et.get("y"))) if et.get("x") is not None else None
        return cls(et.get("kind"), et.text, pos)

    def to_element(self):
        """Convert this object to an Element.

        self.text is ignored, SimpleConstraint.to_string() is used instead.
        """
        element = ET.Element("label", attrib={"kind": self.kind})
        element.text = " && ".join([c.to_string() for c in self.constraints])
        if self.pos is not None:
            element.set("x", str(self.pos[0]))
            element.set("y", str(self.pos[1]))
        return element


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
        """Given a string, construct a SimpleField."""
        self.text = text

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a SimpleField object."""
        return cls(et.text) if et is not None else None

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element.

        This method is meant to be used by derived classes.
        """
        element = ET.Element(self.tag)
        element.text = self.text
        return element


class SystemDeclaration(SimpleField):
    """A derived class for simple strings in UPPAAL.

    See base class SimpleField.
    """

    tag = "system"


class Declaration(SimpleField):
    """A derived class for simple strings in UPPAAL.

    See base class SimpleField.
    """

    tag = "declaration"


class Parameter(SimpleField):
    """A derived class for simple strings in UPPAAL. See class SimpleField."""

    tag = "parameter"


class Name:
    """An object for Name elements in UPPAAL xml files.

    This class is almost identical to the Label class minus the kind attribute.
    'pos' is meaningless for Name attribute of Templates, but we follow the
    UPPAAL xml format regardless.
    """

    def __init__(self, name, pos):
        """Given a string and a pair of ints, construct a Name object."""
        self.name = name
        self.pos = pos

    @classmethod
    def from_element(cls, et):
        """Convert an Element to a Name object."""
        if et is not None:
            if et.get("x") is not None:
                return cls(et.text, (int(et.get("x")), int(et.get("y"))))
            return cls(et.text, None)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element( "name") #, attrib={"x": str(self.pos[0]), "y": str(self.pos[1])})
        element.text = self.name

        if self.pos is not None:
            element.set("x", str(self.pos[0]))
            element.set("y", str(self.pos[1]))

        return element


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
        """Convert an Element to a Query object."""
        return cls(et.find("formula").text, et.find("comment").text)

    def to_element(self):
        """Convert this object to an Element."""
        query = ET.Element("query")
        formula = ET.SubElement(query, "formula")
        formula.text = self.formula
        comment = ET.SubElement(query, "comment")
        comment.text = self.comment
        return query


class SimpleConstraint:
    """Class representing a simple clock constraint.

    Label objects for transition guards and location invariants are actually
    instances of the subclass Constraint of the class Label. They have
    additional attributes for storing a list of SimpleConstraints.

    Attributes:
        clocks: A list of strings with list length either one or two.
            ["x", "y"] denotes x - y and ["x"] simply means x in the LHS
            of the simple constraint.
        operator: String for the comparison operator. Can be '>', '<', or '='.
        threshold: Numeric comparison value.
        equality: Boolean value for determining the whether the clock value
            can be equal to the threshold value, e.g. x < 10 or x <= 10
    """

    def __init__(self, clocks, operator, threshold, equality=False):
        """Construct a SimpleConstraint.

        Arguments:
            clocks: List of strings for clock names.
            operator: String for comparison operator, one of '<', '>', or '='.
            threshold: Numeric value that is used for comparison.
            equality: Bool
        """
        self.clocks = clocks
        self.operator = operator
        self.threshold = threshold
        self.equality = equality

    @classmethod
    def parse_inequality_simple(cls, inequality):
        """Given a simple constraint string, return an SimpleConstraint object."""
        # Taken from
        # https://github.com/jar-ben/tamus/blob/master/uppaalHelpers/timed_automata.py
        ind = 0
        for i in range(len(inequality)):
            if inequality[i] in ["<", ">", "="]:
                ind = i
                break
        lhs = inequality[0:ind].strip()
        operator = inequality[ind]
        equality = False
        if inequality[ind + 1] == "=":
            ind += 1
            equality = True
        rhs = inequality[ind + 1 :].strip()
        threshold = int(rhs)
        clocks = [c.rstrip().strip() for c in lhs.split("-")]
        return cls(clocks, operator, threshold, equality)

    @classmethod
    def parse_inequality(cls, inequality):
        """Split string into simple constraints, return SimpleConstraint list."""
        return [cls.parse_inequality_simple(s) for s in inequality.split("&&")]

    def to_string(self):
        """Convert the object to a string."""
        return " ".join(
            [
                " - ".join(self.clocks),
                self.operator + ("=" if self.equality else ""),
                str(self.threshold),
            ]
        )
