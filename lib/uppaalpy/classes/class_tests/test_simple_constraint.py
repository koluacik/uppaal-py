"""Unit tests for SimpleConstraint class."""

from uppaalpy import SimpleConstraint
import pytest

simple_inequalities = [
    ("x - y < 10", (["x", "y"], "<", 10, False)),
    ("x < 10", (["x"], "<", 10, False)),
    ("x - y >= 2", (["x", "y"], ">", 2, True)),
    ("clock1 == 100", (["clock1"], "=", 100, True)),
]

inequalities = [
    ("x - y < 10 && x > 5", [(["x", "y"], "<", 10, False), (["x"], ">", 5, False)]),
    (
        "x == 3 && y == 10 && z <= 15",
        [(["x"], "=", 3, True), (["y"], "=", 10, True), (["z"], "<", 15, True)],
    ),
]


class TestSimpleConstraint:
    """SimpleConstraint tests."""

    def test_simple_constraint_init(self):
        """Test SimpleConstraint.__init__."""
        simple_constraint1 = SimpleConstraint(["x"], "<", 10)
        assert simple_constraint1.equality == False
        assert simple_constraint1.clocks == ["x"]

        simple_constraint2 = SimpleConstraint(["x", "y"], ">", 13, equality=True)
        assert simple_constraint2.equality == True
        assert simple_constraint2.clocks == ["x", "y"]

    @pytest.mark.parametrize("case", simple_inequalities)
    def test_simple_constraint_parse_inequality_simple(self, case):
        """Test SimpleConstraint.parse_inequality_simple."""
        my_input = case[0]
        expected = case[1]
        my_constraint = SimpleConstraint.parse_inequality_simple(my_input)
        assert my_constraint.clocks == expected[0]
        assert my_constraint.operator == expected[1]
        assert my_constraint.threshold == expected[2]
        assert my_constraint.equality == expected[3]

    @pytest.mark.parametrize("case", inequalities)
    def test_simple_constraint_parse_inequality(self, case):
        """Test SimpleConstraint.parse_inequality."""
        my_input = case[0]
        expected = case[1]
        my_constraint = SimpleConstraint.parse_inequality(my_input)
        assert len(my_constraint) == len(expected)
        for i, cons in enumerate(my_constraint):
            assert cons.clocks == expected[i][0]
            assert cons.operator == expected[i][1]
            assert cons.threshold == expected[i][2]
            assert cons.equality == expected[i][3]

    @pytest.mark.parametrize("case", simple_inequalities)
    def test_simple_constraint_to_string_simple(self, case):
        """Test SimpleConstraint.to_string for singular constraints."""
        assert case[0] == SimpleConstraint.parse_inequality_simple(case[0]).to_string()

    @pytest.mark.parametrize("case", inequalities)
    def test_simple_constraint_to_string(self, case):
        """Test SimpleConstraint.to_string for complex constraints with &&."""
        constraints = SimpleConstraint.parse_inequality(case[0])
        assert case[0] == " && ".join([c.to_string() for c in constraints])