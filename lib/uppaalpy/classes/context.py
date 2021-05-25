"""Class definitions for definitions and declarations in the global scope of the TA."""

from copy import deepcopy
from typing import Dict, List, Optional, Set, Tuple, Type

# from uppaalpy.classes import simplethings as s


class Context:
    """An immutable context that is used for variable lookups.

    Extended by MutableContext, which also provides an interface for updating
    variables during a computation.

    Attributes:
        clocks: A list of clock names.
        constants: A dict from identifier strings to values.
        initial_state: A dict from identifier strings to values.

    Methods:
        empty: Create an empty context.
        is_defined: Check if the identifier is defined in the context.
        is_clock: Check if the identifier is a clock.
        is_constant: Check if the identifier is a constant.
        is_variable: Check if the identifier is a variable.
        get_val: Get the corresponding value of an identifier.
        to_MutableContext: Create a copy of the context to be used in other
            computations.
        parse_context: Given a global declaration string, create a context.
    """

    def __init__(
        self,
        clocks: Set[str],
        constants: Dict[str, int],
        initial_state: Dict[str, int],
    ) -> None:
        """Create a context."""
        self.clocks = clocks
        self.constants = constants
        self.initial_state = initial_state

    @classmethod
    def empty(cls: Type["Context"]) -> "Context":
        """Create an empty context."""
        return cls(set(), {}, {})

    def is_defined(self, identifier: str) -> bool:
        """Return True if the identifier is defined in this context."""
        return (
            self.is_clock(identifier)
            or self.is_constant(identifier)
            or self.is_variable(identifier)
        )

    def is_clock(self, identifier: str) -> bool:
        """Return True if the identifier is a clock."""
        return identifier in self.clocks

    def is_constant(self, identifier: str) -> bool:
        """Return True if the identifier is a constant."""
        return self._is_in(identifier, "constants")

    def is_variable(self, identifier: str) -> bool:
        """Return True if the identifier is a variable."""
        return self._is_in(identifier, "initial_state")

    @staticmethod
    def is_literal(string: str) -> bool:
        """Return True if the given string is a number."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def _is_in(self, identifier: str, attrib: str) -> bool:
        return identifier in getattr(self, attrib).keys()

    def get_val(self, identifier: str) -> int:
        """Return the value of a literal, a constant or a variable.

        Can't be used for clocks.
        """
        if self.is_literal(identifier):
            return int(identifier)
        elif self.is_constant(identifier):
            return self.constants[identifier]
        else:
            return self.initial_state[identifier]

    def to_MutableContext(self) -> "MutableContext":
        """Create a copy of the context to be used in other computations."""
        c = deepcopy(self.clocks)
        const = deepcopy(self.constants)
        init = deepcopy(self.initial_state)
        return MutableContext(c, const, init)

    @classmethod
    def parse_context(cls, declaration: Optional[str]) -> "Context":
        """Get clocks, constants, and variables from global variable.

        Variables of type const int, int, or clock are parsed. Declarations
        should be of form:
        [const] int (identifier "=" value) (identifier "=" value)* ";"
        """
        context = cls.empty()

        if declaration is None:
            return context

        for l in declaration.split("\n"):
            if l.startswith("clock"):
                context._parse_clocks(l)
            elif l.startswith("const int"):
                context._parse_constants(l)
            elif l.startswith("int"):
                context._parse_variables(l)

        return context

    def _parse_clocks(self, line: str) -> None:
        """Given a line starting with "clock" parse clocks."""
        # clock clock1, c2, x; // Some comments...
        #       ^....^  ^^  ^
        for c in line[6 : line.index(";")].split(","):
            self.clocks.add(c.strip())

    def _parse_constants(self, line: str) -> None:
        """Given a line starting with "cont int" parse constants."""
        # const int c = 10, c1 = 100, var; // Some comments...
        #           ^..............,,,,,^
        pairs = self._parse_line(10, line)
        for i, v in pairs:
            self.constants[i] = v

    def _parse_variables(self, line: str) -> None:
        """Given a line starting with "int" parse variables and initial values."""
        # int c = 10, c1 = 100, var; // Some comments...
        #     ^...................^
        pairs = self._parse_line(4, line)
        for i, v in pairs:
            self.initial_state[i] = v

    @staticmethod
    def _parse_line(offset: int, line: str) -> List[Tuple[str, int]]:
        res = []  # type: List[Tuple[str, int]]
        for init in line[offset : line.index(";")].split(","):
            # Declarations with no initialisers are initialized to 0 for ints.
            decl = init.split("=")
            iden = decl[0]
            if len(decl) == 2:
                val = decl[1]
            else:
                val = "0"
            res.append((iden.strip(), int(val.strip())))
        return res


class MutableContext(Context):
    """Mutable version of the Context.

    Properties:
        variables: An alias for the initial_state attribute.

    Methods:
        set_val: Set the value of a variable.
    """

    @property
    def variables(self):
        """Alias for the initial_state attribute."""
        return self.initial_state

    @variables.setter
    def variables(self, x: Dict[str, int]):
        self.initial_state = x

    def set_val(self, identifier: str, val: int):
        """Set the value of a mutable variable."""
        self.variables[identifier] = val
