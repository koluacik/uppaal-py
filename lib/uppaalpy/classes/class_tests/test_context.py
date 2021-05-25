"""Unit tests for Context and MutableContext."""

from uppaalpy.classes.context import Context, MutableContext


class TestContext:
    """Context tests."""

    @staticmethod
    def test_context_init():
        """Test Context initializer."""
        c = Context(set(), {}, {})
        assert c.clocks == set()
        assert c.constants == {}
        assert c.initial_state == {}

        c = Context(set(["foo", "bar"]), {"x": 13, "y": -1}, {"z": 11})

        assert "foo" in c.clocks and "bar" in c.clocks
        assert c.constants["x"] == 13 and c.constants["y"] == -1
        assert c.initial_state["z"] == 11

    @staticmethod
    def test_context_is_clock():
        """Test is_clock method."""
        c = Context(set(), {}, {})
        assert c.is_clock("notclock") == False

        c = Context(set(["foo"]), {}, {})
        assert c.is_clock("foo")

        c = Context(set(["foo", "bar"]), {}, {})
        assert c.is_clock("foo")
        assert c.is_clock("bar")

        c = Context(set(), {"foo": 3}, {"bar": 4})
        assert c.is_clock("foo") == False
        assert c.is_clock("bar") == False

    @staticmethod
    def test_context_is_constant():
        """Test is_constant method."""
        c = Context(set(), {}, {})
        assert c.is_constant("notconstant") == False

        c = Context(set([]), {"foo": 4}, {})
        assert c.is_constant("foo")

    @staticmethod
    def test_context_is_variable():
        """Test is_variable method."""
        c = Context(set(), {}, {})
        assert c.is_variable("notvar") == False

        c = Context(set([]), {}, {"foo": 4})
        assert c.is_variable("foo")

    @staticmethod
    def test_context_is_literal():
        """Test is_literal method."""
        c = Context(set(), {}, {})
        assert c.is_literal("9")

        c = Context(set([]), {}, {"foo": 4})
        assert c.is_literal("hello") == False

    @staticmethod
    def test_context_get_val():
        """Test get_val method."""
        c = Context(set(), {"foo": 3}, {"bar": 4})
        c.get_val("foo") == 3
        c.get_val("bar") == 4
        c.get_val("15") == 15

    @staticmethod
    def test_context_parse_context():
        """Test parse_context method."""
        c = Context.parse_context(
            """
const int x, y = 10; // comment here.
int a = 11, b;
clock c1, c2,c3;
            """
        )
        print(c.clocks, c.constants, c.initial_state, sep="\n")
        assert c.is_constant("x") and c.get_val("x") == 0
        assert c.is_constant("y") and c.get_val("y") == 10

        assert c.is_variable("a") and c.get_val("a") == 11
        assert c.is_variable("b") and c.get_val("b") == 0

        assert c.is_clock("c1") and c.is_clock("c2") and c.is_clock("c3")
        assert not c.is_clock("c4") and not c.is_clock("x") and not c.is_clock("a")


class TestMutableContext:
    """Tests for the MutableContext class."""

    @staticmethod
    def test_mcontext_to_mutable():
        """Test to_MutableContext method of Context."""
        c = Context(set(), {"foo": 3}, {"bar": 4,})
        mc = c.to_MutableContext()

        assert mc.clocks == set()
        assert mc.get_val("foo") == 3
        assert mc.get_val("bar") == 4

        mc.set_val("bar", 1)

        assert mc.get_val("bar") == 1
        assert c.get_val("foo") == 3
        assert c.get_val("bar") == 4

    @staticmethod
    def test_mcontext_variables_property_get():
        """Test is the property works as inteded."""
        c = MutableContext(set(), {"foo": 3}, {"bar": 4})
        assert c.variables["bar"] == 4

    @staticmethod
    def test_mcontext_variables_property_set():
        """Test is the property works as inteded."""
        c = MutableContext(set(), {"foo": 3}, {"bar": 4})
        c.variables["bar"] = 2
        assert c.variables["bar"] == 2

    @staticmethod
    def test_mcontext_set_val():
        """Test set_val."""
        c = MutableContext(set(), {"foo": 3}, {"bar": 4})
        c.set_val("bar", 10)
        assert c.get_val("bar") == 10
