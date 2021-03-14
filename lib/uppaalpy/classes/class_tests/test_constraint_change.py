"""Unit tests for ConstraintChange and its subclasses."""

from uppaalpy.classes.constraint_patcher import (
    ConstraintRemove,
    ConstraintInsert,
    ConstraintChange,
    ConstraintInsert, ConstraintUpdate,
)
from uppaalpy import SimpleConstraint, Constraint
import pytest


class TestConstraintChange:
    """Unit tests for ConstraintChange."""

    def test_constraint_change_init(self):
        """Test initialization of the base class."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cc = ConstraintChange(c)
        assert cc.constraint == c


class TestConstraintRemove:
    """Unit tests for ConstraintRemove."""

    def test_constraint_remove_init(self):
        """Test ConstraintRemove() without specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c, remove_constraint=True)
        assert cr.constraint == c
        assert cr.remove_constraint == True

    def test_constraint_remove_init_remove_false(self):
        """Test ConstraintRemove() with specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c, remove_constraint=False)
        assert cr.constraint == c
        assert cr.remove_constraint == False

    def test_constraint_remove_init_remove_no_remove_arg(self):
        """Test ConstraintRemove() with specifying remove_constraint."""
        c = SimpleConstraint(["x"], ">", 15, False)
        cr = ConstraintRemove(c)
        assert cr.constraint == c
        assert cr.remove_constraint == False

    def test_constraint_remove_find_matching_constraint(self):
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

    def test_constraint_remove_patch_lines_location_basic_without_line_removal(self):
        """Test patch_line method on locations. The invariant will be removed."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5 &amp;&amp; y &lt; 5</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">y &lt; 5</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, False)  # Do not remove invariant label.
        cr.patch_line(lines, 1)

        assert lines == lines_expected

    def test_constraint_remove_patch_lines_location_basic_with_line_removal(self):
        """Test patch_line method on locations. The invariant won't be removed."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            "		</location>",
        ]

        # There is a single constraint on this location. Upon removal of it,
        # invariant label should be deleted as well.
        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)  # Remove invariant label.
        cr.patch_line(lines, 1)

        assert lines == lines_expected

    def test_constraint_remove_patch_lines_location_with_other_labels(self):
        """Test patch_line method on locations with other labels."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="name" x="18" y="-34">location0</label>',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="name" x="18" y="-34">location0</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 2)

        assert lines == lines_expected

        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="name" x="18" y="-34">location0</label>',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5</label>',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="name" x="18" y="-34">location0</label>',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["x"], "<", 5, False)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 2)

        assert lines == lines_expected

    def test_constraint_remove_patch_lines_transition(self):
        """Test patch_line method on transitions."""
        lines = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock == 5</label>',
            "		</transition>",
        ]

        lines_expected = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            "		</transition>",
        ]

        c = SimpleConstraint(["x"], "=", 5, True)
        cr = ConstraintRemove(c, True)
        cr.patch_line(lines, 3)

        assert lines == lines_expected

        lines = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; clock == 5</label>',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>',
            "		</transition>",
        ]

        lines_expected = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock2 == 5</label>',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>',
            "		</transition>",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        cr = ConstraintRemove(c, False)
        cr.patch_line(lines, 3)

        assert lines == lines_expected


class TestConstraintInsert:
    """Unit tests for ConstraintInsert."""

    def test_constraint_insert_init(self):
        """Test ConstraintInsert()."""
        c = SimpleConstraint(["x", "y"], "<", 5, True)
        ci = ConstraintInsert(c)
        assert ci.constraint == c
        assert ci.newly_created == None

    def test_constraint_insert_init_with_new(self):
        """Test ConstraintInsert(), with newly_created set."""
        c = SimpleConstraint(["x", "y"], "<", 5, True)
        guard = Constraint("invariant", "", (0, 0), [c])
        ci = ConstraintInsert(c, guard)
        assert ci.constraint == c
        assert ci.newly_created == guard

    def test_constraint_insert_patch_lines_location_basic_no_prior_invariant(self):
        """Test patch_line on locations, creating a new invariant."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["x", "y"], "<", 5, True)
        invariant = Constraint("invariant", "", (18, -34), [c])
        ci = ConstraintInsert(c, invariant)
        ci.patch_line(lines, 0, 0)

        assert lines == lines_expected

    def test_constraint_insert_patch_lines_location_basic_with_prior_invariant(self):
        """Test patch_line on locations, without creating a new invariant."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5 &amp;&amp; c == 3</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["c"], "=", 3, True)
        ci = ConstraintInsert(c)
        ci.patch_line(lines, 1, 0)

        assert lines == lines_expected

    def test_constraint_insert_patch_lines_transition(self):
        """Test patch_line on transitions."""
        lines = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            "		</transition>",
        ]

        lines_expected = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock == 5</label>',
            "		</transition>",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        guard = Constraint("guard", "", (18, -34), [c])
        ci = ConstraintInsert(c, guard)
        ci.patch_line(lines, 2, 0)

        assert lines == lines_expected

        lines = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock2 == 5</label>',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>',
            "		</transition>",
        ]

        lines_expected = [
            "		<transition>",
            '			<source ref="id0"/>',
            '			<source ref="id1"/>',
            '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; clock == 5</label>',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>',
            "		</transition>",
        ]

        c = SimpleConstraint(["clock"], "=", 5, True)
        ci = ConstraintInsert(c)
        ci.patch_line(lines, 3, 0)

        assert lines == lines_expected


class TestConstraintUpdate:
    """Unit tests for ConstraintUpdate."""

    def test_constraint_update_init(self):
        """Test ConstraintUpdate()."""
        c = SimpleConstraint(["x"], ">", 13, False)
        cu = ConstraintUpdate(c, 10, 13)

        assert cu.constraint == c
        assert cu.old == 10
        assert cu.new == 13

    def test_constraint_update_find_matching_constraint(self):
        """Test _find_matching_constraint method."""
        c = SimpleConstraint(["x"], ">", 13, False)
        cu = ConstraintUpdate(c, 10, 13)

        constraints1 = ["x &gt; 10"]
        constraints2 = ["x == 10", "x &gt; 10"]
        constraints3 = ["x &gt; 13"]

        assert cu._find_matching_constraint(constraints1) == 0
        assert cu._find_matching_constraint(constraints2) == 1
        with pytest.raises(Exception):
            assert cu._find_matching_constraint(constraints3)

    def test_constraint_update_patch_line_location(self):
        """Test patch_line method on locations."""
        lines = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x &lt; 5 &amp;&amp; y &lt; 5</label>',
            "		</location>",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">',
            '			<label kind="invariant" x="18" y="-34">x &lt; 10 &amp;&amp; y &lt; 5</label>',
            "		</location>",
        ]

        c = SimpleConstraint(["x"], "<", 10, False)
        cu = ConstraintUpdate(c, 5, 10)  # Replace threshold 5 with 10.
        cu.patch_line(lines, 1)

        assert lines == lines_expected

