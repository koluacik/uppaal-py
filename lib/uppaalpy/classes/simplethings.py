"""Basic classes used by other classes throughout the project."""

from typing import List, Optional, Tuple, Type, TypeVar

import lxml.etree as ET

from uppaalpy.classes import context as c
from uppaalpy.classes import expr as e

PosType = Tuple[int, int]
Constraints = List[e.ConstraintExpression]
Updates = List[e.UpdateExpression]

L = TypeVar("L", bound="Label")


class Label:
    """A label object from UPPAAL.

    Many location and edge attributes in UPPAAL are stored as xml elements with
    tag 'label', and differentiated by their attribute 'kind'. Finally, they
    also have a location 'x' and 'y'. Some label kinds like test code are not
    visible in the UPPAAL template editor. These labels do not have a pos.

    See subclass ConstraintLabel and UpdateLabel.

    Attributes:
        kind: String for differentiating the kind of the label.
        value: String for storing the content of the label.
        pos: A pair of ints for position. Some label kinds do not have a pos.
    """

    def __init__(self, kind: str, value: str, pos: Optional[PosType] = None) -> None:
        """Construct a Label object given kind, value, and optional pos.

        For invariants and guards, subclass ConstraintLabel is used.
        For clock resets and other updates during a transition, subclass
        UpdateLabel is used.

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
    def from_element(cls: Type[L], et) -> L:
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


class ConstraintLabel(Label):
    """A specific label for invariants or transitions in timed automata.

    The attribute constraints is a list ConstraintExpressions.
    It simplifies computations involving constraints. This class overrides
    the Label.to_element() and Label.from_element() methods. self.value
    is ignored after initialization. Also see class ConstraintExpression

    Extra Attributes:
        constraints: List of ConstraintExpression
    """

    def __init__(
        self,
        kind: str,
        value: str,
        pos: Optional[PosType],
        ctx: c.Context,
        constraints: Optional[Constraints] = None,
    ) -> None:
        """Construct a ConstraintLabel from Label args, and constraints.

        If a constraints is None, the value attribute is parsed, instead.

        Args:
            kind: String denoting the kind of the constraint. Must be "guard"
                or "invariant".
            value: String denoting the text content of the Label.
            pos: Pair of ints for the position of the Label.
            ctx: Context object to lookup declarations.
            constraints: List of ConstraintExpression objects. If None
                (default), value is parsed, instead.
        """
        super().__init__(kind, value, pos)
        self.constraints: Constraints = (
            constraints
            if constraints
            else [
                e.ConstraintExpression.parse_expr(s, ctx)  # Factory
                for s in e.ConstraintExpression.split_into_simple(value)
            ]
        )

    @classmethod
    def from_label(
        cls: Type["ConstraintLabel"],
        label: Label,
        ctx: c.Context,
        constraints: Optional[Constraints] = None,
    ) -> "ConstraintLabel":
        """Construct a ConstraintLabel from a Label object.

        Args:
            label: A label object.
            ctx: Context object.
            constraints: List of ConstraintExpression objects. If None
                (default), value field of the label is parsed, instead.
        """
        return cls(label.kind, label.value, label.pos, ctx, constraints)

    @classmethod
    def from_element(
        cls: Type["ConstraintLabel"], et, ctx: c.Context
    ) -> "ConstraintLabel":
        """Convert an Element to a ConstraintLabel."""
        pos = (int(et.get("x")), int(et.get("y"))) if et.get("x") is not None else None
        return cls(et.get("kind"), et.text, pos, ctx)

    def to_element(self):
        """Convert this object to an Element.

        self.text is ignored, ConstraintExpression.to_string() is used instead.
        """
        element = ET.Element("label", attrib={"kind": self.kind})
        element.text = e.ConstraintExpression.join_expressions(self.constraints)
        if self.pos is not None:
            element.set("x", str(self.pos[0]))
            element.set("y", str(self.pos[1]))
        return element


class UpdateLabel(Label):
    """A specific label for updates on transitions in timed automata.

    The attribute updates is a list of UpdateExpressions.
    This Class overrides the Label.to_element() and from_element() methods.
    self.value is ignored after initialization. Also see class UpdateExpression.

    Attributes:
        updates: List of UpdateExpression.
    """

    def __init__(
        self,
        kind: str,
        value: str,
        pos: Optional[PosType],
        ctx: c.Context,
        updates: Optional[Updates] = None,
    ) -> None:
        """Construct a UpdateLabel from Label args, and updates.

        If updates is None, the value attribute is parsed, instead.

        Args:
            kind: String denoting the kind of the update. Must be "assignment".
            value: String denoting the text content of the Label.
            pos: Pair of ints for the position of the Label.
            ctx: Context object for looking up declarations.
            updates: List of UpdateExpression objects. If None (default), value
                is parsed, instead.
        """
        super().__init__(kind, value, pos)
        self.updates = (
            updates
            if updates
            else [
                e.UpdateExpression.parse_expr(s, ctx)
                for s in e.UpdateExpression.split_into_simple(value)
            ]
        )

    @classmethod
    def from_label(
        cls: Type["UpdateLabel"],
        label: Label,
        ctx: c.Context,
        updates: Optional[Updates] = None,
    ) -> "UpdateLabel":
        """Construct a UpdateLabel from a Label object.

        Args:
            label: A label object.
            ctx: Context object.
            constraints: List of UpdateExpression objects. If None
                (default), value field of the label is parsed, instead.
        """
        return cls(label.kind, label.value, label.pos, ctx, updates)

    @classmethod
    def from_element(cls: Type["UpdateLabel"], et, ctx: c.Context) -> "UpdateLabel":
        """Convert an Element to an UpdateLabel."""
        pos = (int(et.get("x")), int(et.get("y"))) if et.get("x") is not None else None
        return cls(et.get("kind"), et.text, pos, ctx)

    def to_element(self):
        """Convert this object to an Element.

        self.text is ignored, UpdateExpression.to_string() is used instead.
        """
        element = ET.Element("label", attrib={"kind": self.kind})
        element.text = e.UpdateExpression.join_expressions(self.updates)
        if self.pos is not None:
            element.set("x", str(self.pos[0]))
            element.set("y", str(self.pos[1]))
        return element

    def get_resets(self) -> List[str]:
        """Return list of clocks to be reset."""
        res = []
        for expr in self.updates:
            if isinstance(expr, e.ClockResetExpression):
                if expr.clock not in res:
                    res.append(expr.clock)
        return res

    def get_other_updates(self) -> List[e.UpdateExpression]:
        """Return UpdateExpressions that are not clock resets."""
        res = []
        for expr in self.updates:
            if not isinstance(expr, e.ClockResetExpression):
                res.append(expr)
        return res


T = TypeVar("T", bound="SimpleField")


class SimpleField:
    """Simple text field with fromEt and to_element methods.

    This class can be thought of as a abstract class for strings with no
    extra information in UPPAAL. It is a base class for other classes
    SystemDeclaration, Declaration, and Parameter. They only differ by their
    class attribute tag. This way we can easily serialize different types of
    text fields to xml.
    """

    tag = ""

    def __init__(self, text: str) -> None:
        """Given a string, construct a SimpleField."""
        self.text = text

    @classmethod
    def from_element(cls: Type[T], et) -> Optional[T]:
        """Convert an Element to a SimpleField object."""
        if et is None:
            return None
        elif et.text is None:
            return cls("")
        else:
            return cls(et.text)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element.

        This method is meant to be used by derived classes.
        """
        element = ET.Element(self.tag)
        element.text = self.text
        return element


class SystemDeclaration(SimpleField):
    """A derived class for simple strings in UPPAAL. Contains the system declaration.

    See base class SimpleField.
    """

    tag = "system"


class Declaration(SimpleField):
    """A derived class for simple strings in UPPAAL.

    Contains the declarations of constants, variables, and clocks of
    the system and the templates.

    Can be parsed by Context class to generate a context.

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

    def __init__(self, name: str, pos: Optional[Tuple[int, int]]) -> None:
        """Given a string and a pair of ints, construct a Name object."""
        self.name = name
        self.pos = pos

    @classmethod
    def from_element(cls: Type["Name"], et) -> Optional["Name"]:
        """Convert an Element to a Name object."""
        if et is not None:
            if et.get("x") is not None:
                return cls(et.text, (int(et.get("x")), int(et.get("y"))))
            return cls(et.text, None)

    def to_element(self):
        """Convert this object to an Element. Called from NTA.to_element."""
        element = ET.Element("name")
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

    def __init__(self, formula: str, comment: str) -> None:
        """Query object initializer."""
        self.formula = formula
        self.comment = comment

    @classmethod
    def from_element(cls: Type["Query"], et) -> "Query":
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
