"""Unit tests for the Constraint class."""
import lxml.etree as ET
import pytest

from uppaalpy import Constraint, Label, SimpleConstraint

from .helpers import list_xml_in_dir, testcase_dir


@pytest.fixture(params=["guard", "invariant"])
def label_kind(request):
    """Fixture for label kinds."""
    return request.param


@pytest.fixture(params=[(1, 2), (-100, 15)])
def label_pos(request):
    """Fixture for label positions."""
    return request.param


constraint_strings = [
    "clock1 >= 15",
    "clock1 <= 16 && clock1 > 7",
    "x - y == 15 && z < 13 && p < 14",
]


@pytest.fixture(params=constraint_strings)
def label_value(request):
    """Fixture for constraint values."""
    return request.param


@pytest.fixture
def label_constraints(label_value):
    """Fixture for constraint lists."""
    return SimpleConstraint.parse_inequality(label_value)


@pytest.fixture
def label(label_kind, label_value, label_pos):
    """Fixture for generating labels."""
    return Label(label_kind, label_value, label_pos)


@pytest.fixture(params=list_xml_in_dir(testcase_dir + "constraint_xml_files"))
def constraint_element(request):
    """Fixture for Constraint Elements."""
    return ET.parse(request.param).getroot()


class TestConstraint:
    """Constraint tests."""

    def test_constraint_init_without_constraints(
        self, label_kind, label_pos, label_value
    ):
        """Test Constraint.__init__ by parsing value attribute."""
        c = Constraint(label_kind, label_value, label_pos)
        assert c.to_element().text == label_value

    def test_constraint_init_with_constraints(
        self, label_kind, label_pos, label_value, label_constraints
    ):
        """Test Constraint.__init__, with provided constraints."""
        c1 = Constraint(
            label_kind, label_value, label_pos, label_constraints
        ).constraints
        c2 = Constraint(label_kind, label_value, label_pos).constraints

        assert len(c1) == len(c2)

        for sc1, sc2 in zip(c1, c2):
            assert sc1.clocks == sc2.clocks
            assert sc1.equality == sc2.equality
            assert sc1.operator == sc2.operator
            assert sc1.threshold == sc2.threshold

    def test_constraint_from_label_without_constrains(self, label):
        """Test converting Label to Constraint."""
        c = Constraint.from_label(label)
        assert c.kind == label.kind
        assert c.pos == label.pos
        assert " && ".join([x.to_string() for x in c.constraints]) == label.value

    def test_constraint_from_label_with_constraints(self, label, label_constraints):
        """Test converting Label to Constraint with additional constraints."""
        c = Constraint.from_label(label, label_constraints)
        assert c.kind == label.kind
        assert c.pos == label.pos
        assert " && ".join([x.to_string() for x in c.constraints]) == label.value

    def test_constraint_from_element(self, constraint_element):
        """Test Contraint.from_element."""
        c = Constraint.from_element(constraint_element)
        assert c.kind == constraint_element.get("kind")
        assert str(c.pos[0]) == constraint_element.get("x")
        assert str(c.pos[1]) == constraint_element.get("y")
        assert c.value == constraint_element.text
        properly_spaced_inequality = " && ".join([x.to_string() for x in c.constraints])
        inequality = properly_spaced_inequality.replace(" ", "")
        assert inequality == constraint_element.text.replace(" ", "")

    def test_constraint_to_element(self, constraint_element):
        """Test Constraint.to_element."""
        c_element = Constraint.from_element(constraint_element).to_element()
        assert c_element.get("kind") == constraint_element.get("kind")
        assert c_element.get("x") == constraint_element.get("x")
        assert c_element.get("y") == constraint_element.get("y")
        assert c_element.text.replace(
            " ", ""
        ) == constraint_element.text.replace(" ", "")
