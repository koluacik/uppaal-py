"""Unit tests for ConstraintChange and its subclasses."""

import pytest

from uppaalpy import Constraint, SimpleConstraint
from uppaalpy.classes.constraint_patcher import (
    ConstraintChange,
    ConstraintInsert,
    ConstraintInsert,
    ConstraintRemove,
    ConstraintUpdate,
)


class TestConstraintChange:
    """Unit tests for ConstraintChange."""

    @staticmethod
    def test_constraint_change_init():
        """Test initialization of the base class."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cc = ConstraintChange(c)
        assert cc.constraint == c


class TestConstraintRemove:
    """Unit tests for ConstraintRemove."""

    @staticmethod
    def test_constraint_remove_init():
        """Test ConstraintRemove() without specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c, remove_constraint=True)
        assert cr.constraint == c
        assert cr.remove_constraint == True

    @staticmethod
    def test_constraint_remove_init_remove_false():
        """Test ConstraintRemove() with specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c, remove_constraint=False)
        assert cr.constraint == c
        assert cr.remove_constraint == False

    @staticmethod
    def test_constraint_remove_init_remove_no_remove_arg():
        """Test ConstraintRemove() with specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c)
        assert cr.constraint == c
        assert cr.remove_constraint == False

    @staticmethod
    def test_constraint_remove_find_matching_constraint():
        """Test ConstraintRemove._find_matching_constraint."""
        c = SimpleConstraint(["clock1", "clock2"], "<", 15)
        cr = ConstraintRemove(c)

        constraints1 = ["x - y&lt;13", "clock1-clock2&lt;15"]
        constraints2 = ["x - y&lt;13", "clock1 - clock2 &lt; 15"]
        constraints3 = ["x - y&lt;13"]  # Should raise Exception.

        assert cr._find_matching_constraint(constraints1) == 1
        assert cr._find_matching_constraint(constraints2) == 1
        with pytest.raises(Exception):
            assert cr._find_matching_constraint(constraints3)

    @staticmethod
    def test_constraint_remove_patch_lines_location_basic_without_line_removal():
        """Test patch_line method on locations. The invariant will be removed."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5 &amp;&amp; y &lt; 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">y &lt; 5</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, False)  # Do not remove invariant label.
        cr.patch_line(lines, 1)

        assert lines == lines_expected

    @staticmethod
    def test_constraint_remove_patch_lines_location_basic_with_line_removal():
        """Test patch_line method on locations. The invariant won't be removed."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            "		</location>\n",
        ]

        # There is a single constraint on this location. Upon removal of it,
        # invariant label should be deleted as well.
        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)  # Remove invariant label.
        cr.patch_line(lines, 1)

        assert lines == lines_expected

    @staticmethod
    def test_constraint_remove_patch_lines_location_with_other_labels():
        """Test patch_line method on locations with other labels."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 2)

        assert lines == lines_expected

        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>\n',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 2)

        assert lines == lines_expected

    @staticmethod
    def test_constraint_remove_patch_lines_transition():
        """Test patch_line method on transitions."""
        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock == 5</label>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            "		</transition>\n",
        ]

        c = SimpleConstraint(["x"], "=", 5, True)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 3)

        assert lines == lines_expected

        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; clock == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        cr = ConstraintRemove(c, False)
        cr.patch_line(lines, 3)

        assert lines == lines_expected


class TestConstraintInsert:
    """Unit tests for ConstraintInsert."""

    @staticmethod
    def test_constraint_insert_init():
        """Test ConstraintInsert()."""
        c = SimpleConstraint(["x", "y"], "<", 5, True)
        ci = ConstraintInsert(c)
        assert ci.constraint == c
        assert ci.newly_created == None

    @staticmethod
    def test_constraint_insert_init_with_new():
        """Test ConstraintInsert(), with newly_created set."""
        c = SimpleConstraint(["x", "y"], "<", 5, True)
        guard = Constraint("invariant", "", (0, 0), [c])
        ci = ConstraintInsert(c, guard)
        assert ci.constraint == c
        assert ci.newly_created == guard

    @staticmethod
    def test_constraint_insert_patch_lines_location_basic_no_prior_invariant():
        """Test patch_line on locations, creating a new invariant."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["x", "y"], "<", 5, True)
        invariant = Constraint("invariant", "", (18, -34), [c])
        ci = ConstraintInsert(c, invariant)
        ci.patch_line(lines, 0, 0)

        assert lines == lines_expected

    @staticmethod
    def test_constraint_insert_patch_lines_location_basic_with_prior_invariant():
        """Test patch_line on locations, without creating a new invariant."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5 &amp;&amp; c == 3</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["c"], "=", 3, True)
        ci = ConstraintInsert(c)
        ci.patch_line(lines, 1, 0)

        assert lines == lines_expected

    @staticmethod
    def test_constraint_insert_patch_lines_transition():
        """Test patch_line on transitions."""
        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock == 5</label>\n',
            "		</transition>\n",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        guard = Constraint("guard", "", (18, -34), [c])
        ci = ConstraintInsert(c, guard)
        ci.patch_line(lines, 2, 0)

        assert lines == lines_expected

        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; clock == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        ci = ConstraintInsert(c)
        ci.patch_line(lines, 3, 0)

        assert lines == lines_expected


class TestConstraintUpdate:
    """Unit tests for ConstraintUpdate."""

    @staticmethod
    def test_constraint_update_init():
        """Test ConstraintUpdate()."""
        c = SimpleConstraint(["x"], ">", 10, False)
        cu = ConstraintUpdate(c, 13)

        assert cu.constraint == c
        assert cu.old == 10
        assert cu.new == 13

    @staticmethod
    def test_constraint_update_find_matching_constraint():
        """Test _find_matching_constraint method."""
        c = SimpleConstraint(["x"], ">", 10, False)
        cu = ConstraintUpdate(c, 13)

        constraints1 = ["x &gt; 10"]
        constraints2 = ["x == 10", "x &gt; 10"]
        constraints3 = ["x &gt; 13"]

        assert cu._find_matching_constraint(constraints1) == 0
        assert cu._find_matching_constraint(constraints2) == 1
        with pytest.raises(Exception):
            assert cu._find_matching_constraint(constraints3)

    @staticmethod
    def test_constraint_update_patch_line_location():
        """Test patch_line method on locations."""
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5 &amp;&amp; y &lt; 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x &lt; 10 &amp;&amp; y &lt; 5</label>\n',
            "		</location>\n",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cu = ConstraintUpdate(c, 10)  # Replace threshold 5 with 10.
        cu.patch_line(lines, 1)

        assert lines == lines_expected
