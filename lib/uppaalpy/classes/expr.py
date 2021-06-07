"""Classes for representing various expressions."""

from abc import ABCMeta, abstractmethod
from typing import List, Literal, Sequence, Tuple, TypeVar, Union

from uppaalpy.classes import context as c # import Context, MutableContext

E = TypeVar("E", bound="Expression")


class Expression(metaclass=ABCMeta):
    """Abstact base class representing expressions.

    An expression can either be an update to the current variables or
    evaluate to a boolean value. Currently, not all expressions in UPPAAL
    are allowed. For details, see child classes ConstraintExpression and
    UpdateExpression.

    Attributes:
        delimiter: Delimiter used for splitting/joining complex expressions.
        lhs: Left hand side of the expression.
        op: Operator
        rhs: Right hand side of the expression

    Methods:
        get_delimiter: Delimiter used for splitting/joining complex expressions.
        tokenize: Default method for tokenizing the input string. Returns
            lhs, op, and rhs.
        parse_expr: Parse an expression string and generate an Expression.
        to_string: Convert the expression to a string.
        split_into_simple: Split a string into substrings delimited by the
            given delimiter.
        join_expressions: Join a sequence of simple expressions into one
            complex expression string.
        join_strings: Join a sequence of simple expression strings into one
            complex expression string.
    """

    delimiter: str = ""

    def __init__(self, exprstr: str, ctx: c.Context, ops: Sequence[str] = "=<>!+-") -> None:
        """Create Expression with lhs, op, and rhs from an expression string."""
        self.lhs, self.op, self.rhs = self.tokenize(exprstr, ops)

    @staticmethod
    def tokenize(string: str, ops: Sequence[str] = "=<>!+-") -> Tuple[str, str, str]:
        """Tokenize the input string.

        Returns a tuple of strings of the form (lhs, op, rhs).

        Args:
            string: The expression string.
            ops: Valid operator characters.

        Returns:
            A 3-tuple of strings.
        """
        lhs, op, rhs = "", "", ""

        # foo <= bar
        for i, c in enumerate(string):
            if c in ops:
                op = c
                nextc = string[i + 1]
                lhs = string[:i].strip()
                rhs = string[i + 1 :].strip()
                if nextc in ops:  # if
                    op += nextc
                    rhs = rhs[1:].strip()
                break
        return lhs, op, rhs

    @classmethod
    @abstractmethod
    def parse_expr(cls, string: str, ctx: c.Context) -> "Expression":
        """Parse an expression string and generate an Expression."""
        pass

    def to_string(self) -> str:
        """Convert the expression back to a string."""
        return " ".join([self.lhs, self.op, self.rhs])

    @classmethod
    def split_into_simple(cls, complex_str: str) -> List[str]:
        """Split a complex expression into simple expression strings."""
        return complex_str.split(cls.delimiter.strip())

    @classmethod
    def join_expressions(cls, exprs: List[E]) -> str:
        """Join a sequence of simple expressions into one expression string."""
        return cls.join_strings([expr.to_string() for expr in exprs])

    @classmethod
    def join_strings(cls, exprstrs: List[str]) -> str:
        """Join a sequence of simple expressions into one expression string."""
        return cls.delimiter.join(exprstrs)


class UpdateExpression(Expression):
    """Class representing updates when a transition is taken.

    Many UpdateExpressions can be delimited by ", " forming complex
    update expressions. Multiplw updates are executed from left to right.
    For instance, "x = 10, y += x" increments y by 10.

    lhs must be a mutable variable (int). op can be =, +=, or -=.
    rhs can be a constant, a variable, or an int.

    Is extended by ClockResetExpression.
    """

    delimiter = ", "

    @classmethod
    def parse_expr(cls, string: str, ctx: c.Context) -> "UpdateExpression":
        """Construct UpdateExpression with some polymorphism."""
        lhs, _, _ = cls.tokenize(string)
        if ctx.is_clock(lhs):
            return ClockResetExpression(string, ctx)
        return cls(string, ctx)

    def handle_update(self, ctx: c.MutableContext) -> None:
        """Update the mutable context with this expression."""
        cur = ctx.get_val(self.lhs)

        {
            "=": lambda rhs: ctx.set_val(self.lhs, rhs),
            "+=": lambda rhs: ctx.set_val(self.lhs, cur + rhs),
            "-=": lambda rhs: ctx.set_val(self.lhs, cur - rhs),
        }[self.op](ctx.get_val(self.rhs))


class ClockResetExpression(UpdateExpression):
    """Class representing clock resets.

    Extends UpdateExpression with the additional "clock" attribute.
    """

    def __init__(self, exprstr: str, _ctx: c.Context) -> None:
        """Create a ClockResetExpression."""
        super().__init__(exprstr, _ctx)
        self.clock: str = self.lhs


class ConstraintExpression(Expression):
    """Class representing simple constraints.

    Conjunction (&&) of one or more simple constraints constitute a
    complex constraint, used in guards and invariants.

    One of the sides of the expression (lhs or rhs) must INCLUDE either a clock
    or a variable (Note that since clock difference is also supported for clock
    constraints, lhs and rhs should be split further to discover clocks in clock
    difference expressions such as "x - y <= 10".). The other side can be a
    constant, a variable, or an int.  The operator can be <, <=, ==, >=, or >.

    Extends Expression class.
    Extended by ClockConstraintExpression for clock constraints.

    For clock constraints ClockConstraint class should be used. When the type
    of a constaint expression is not known in advance, parse_expr method
    instead of __init__ should be used since parse_expr method automatically
    constructs the ClockConstraint's initializer.
    """

    delimiter = " && "

    @classmethod
    def parse_expr(cls, string: str, ctx: c.Context) -> "ConstraintExpression":
        """Parse an expression string and generate an Expression."""
        lhs, _, rhs = cls.tokenize(string, "<>=")
        for x in lhs.split("-") + rhs.split("-"):
            if ctx.is_clock(x.strip()):
                return ClockConstraintExpression(string, ctx)
        return cls(string, ctx)

    def handle_constraint(self, ctx: c.Context) -> bool:
        """Evaluate the constraint expression based on the current context."""
        return {
            "<": lambda lhs, rhs: lhs < rhs,
            "<=": lambda lhs, rhs: lhs <= rhs,
            "==": lambda lhs, rhs: lhs == rhs,
            ">=": lambda lhs, rhs: lhs >= rhs,
            ">": lambda lhs, rhs: lhs > rhs,
        }[self.op](ctx.get_val(self.lhs), ctx.get_val(self.rhs))


class ClockConstraintExpression(ConstraintExpression):
    """Base class for representing simple clock constraints.

    Attributes:
        clocks: A list of strings with list length either one or two.
            ["x", "y"] denotes x - y and ["x"] simply means x in the simple
            constraint.
        operator: String for the comparison operator. Can be '>', '<', or '='.
        equality: Boolean value for determining the whether the clock value
            can be equal to the threshold value, e.g. x < 10 or x <= 10
        threshold: The value the clock (or clock difference) is constrained by.
            Actually, is a property that "points to" lhs or rhs.
        _threshold_side: Either "left" or "right", used by the threshold property.
    """

    def __init__(self, string: str, ctx: c.Context) -> None:
        """Construct a clock constraint."""
        super().__init__(string, ctx, "<>=")
        self._threshold_side: Union[Literal["left"], Literal["right"]]
        self.clocks: List[str]

        # Determine which side the threshold is.
        if (
            ctx.is_constant(self.lhs)
            or ctx.is_literal(self.lhs)
            or ctx.is_variable(self.lhs)
        ):
            self._threshold_side = "left"
            self.clocks = [c.strip() for c in self.rhs.split("-")]
        else:
            self._threshold_side = "right"
            self.clocks = [c.strip() for c in self.lhs.split("-")]

        self.operator = self.op[0]
        self.equality = len(self.op) == 2

    @property
    def threshold(self):
        if self._threshold_side == "left":
            return self.lhs
        else:
            return self.rhs

    @threshold.setter
    def threshold(self, val):
        if self._threshold_side == "left":
            self.lhs = val
        else:
            self.rhs = val

    def handle_constraint(self, _: c.Context) -> bool:
        """Evaluate the constraint expression based on the current context."""
        raise Exception("ClockConstraints can't be statically checked.")

    def to_string(self, escape=False) -> str:
        """Convert the object to a string.

        If escape is True '<', '>', etc. will be escaped to make the
        resulting string xml-friendly.
        """
        if self.equality:
            self.operator += "="
        res = super().to_string()
        if escape:
            res = (
                res.replace("&", "&amp;")
                .replace('"', "&apos;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("'", "&quot;")
            )
        return res
