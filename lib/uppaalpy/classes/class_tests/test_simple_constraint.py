"""Unit tests for SimpleConstraint class."""

import pytest

from uppaalpy import SimpleConstraint

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

    @staticmethod
    def test_simple_constraint_init():
        """Test SimpleConstraint.__init__."""
        simple_constraint1 = SimpleConstraint(["x"], "<", 10)
        assert simple_constraint1.equality == False
        assert simple_constraint1.clocks == ["x"]

        simple_constraint2 = SimpleConstraint(["x", "y"], ">", 13, equality=True)
        assert simple_constraint2.equality == True
        assert simple_constraint2.clocks == ["x", "y"]

    @staticmethod
    @pytest.mark.parametrize("case", simple_inequalities)
    def test_simple_constraint_parse_inequality_simple(case):
        """Test SimpleConstraint.parse_inequality_simple."""
        my_input = case[0]
        expected = case[1]
        my_constraint = SimpleConstraint.parse_inequality_simple(my_input)
        assert my_constraint.clocks == expected[0]
        assert my_constraint.operator == expected[1]
        assert my_constraint.threshold == expected[2]
        assert my_constraint.equality == expected[3]

    @staticmethod
    @pytest.mark.parametrize("case", inequalities)
    def test_simple_constraint_parse_inequality(case):
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

    @staticmethod
    @pytest.mark.parametrize("case", simple_inequalities)
    def test_simple_constraint_to_string_simple(case):
        """Test SimpleConstraint.to_string for singular constraints."""
        assert case[0] == SimpleConstraint.parse_inequality_simple(case[0]).to_string()

    @staticmethod
    @pytest.mark.parametrize("case", inequalities)
    def test_simple_constraint_to_string(case):
        """Test SimpleConstraint.to_string for complex constraints with &&."""
        constraints = SimpleConstraint.parse_inequality(case[0])
        assert case[0] == " && ".join([c.to_string() for c in constraints])
