"""Unit tests for ConstraintChange and its subclasses."""

import pytest
from pytest_cases.case_parametrizer_new import parametrize_with_cases

# from uppaalpy import ConstraintLabel, ClockConstraintExpression
from uppaalpy.classes.class_tests.test_constraint_change_cases import (
    CaseCRInit,
    CaseRFind,
    CaseRPatch,
)
# from uppaalpy.classes.class_tests.test_context_cases import DataContext
from uppaalpy.classes.constraint_patcher import (
    # ConstraintChange,
    # ConstraintInsert,
    # ConstraintInsert,
    ConstraintRemove,
    # ConstraintUpdate,
)


class TestConstraintRemove:
    @parametrize_with_cases("exp, rem", cases=CaseCRInit)
    def test_init(self, exp, rem):
        if rem == None:
            cr = ConstraintRemove(exp)
            assert cr.remove_label == False
        else:
            cr = ConstraintRemove(exp, remove_label=rem)
            assert cr.remove_label == rem

        assert cr.constraint == exp

    @parametrize_with_cases("exp, lst, res", cases=CaseRFind)
    def test_find(self, exp, lst, res):
        cr = ConstraintRemove(exp)

        if res == -1:
            with pytest.raises(Exception):
                assert cr._find_matching_constraint(lst)
        else:
            assert cr._find_matching_constraint(lst) == res

    @parametrize_with_cases("cr, lines, index, res", cases=CaseRPatch)
    def test_patch(self, cr, lines, index, res):
        cr.patch_line(lines, index)
        assert lines == res


# class TestConstraintInsert:
#     """Unit tests for ConstraintInsert."""
#
#     @staticmethod
#     def test_constraint_insert_init():
#         """Test ConstraintInsert()."""
#         c = ClockConstraintExpression(["x", "y"], "<", 5, True)
#         ci = ConstraintInsert(c)
#         assert ci.constraint == c
#         assert ci.newly_created == None
#
#     @staticmethod
#     def test_constraint_insert_init_with_new():
#         """Test ConstraintInsert(), with newly_created set."""
#         c = ClockConstraintExpression(["x", "y"], "<", 5, True)
#         guard = ConstraintLabel("invariant", "", (0, 0), [c])
#         ci = ConstraintInsert(c, guard)
#         assert ci.constraint == c
#         assert ci.newly_created == guard
#
#     @staticmethod
#     def test_constraint_insert_patch_lines_location_basic_no_prior_invariant():
#         """Test patch_line on locations, creating a new invariant."""
#         lines = [
#             '		<location id="id0" x="0" y="0">\n',
#             "		</location>\n",
#         ]
#
#         lines_expected = [
#             '		<location id="id0" x="0" y="0">\n',
#             '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>\n',
#             "		</location>\n",
#         ]
#
#         c = ClockConstraintExpression(["x", "y"], "<", 5, True)
#         invariant = ConstraintLabel("invariant", "", (18, -34), [c])
#         ci = ConstraintInsert(c, invariant)
#         ci.patch_line(lines, 0, 0)
#
#         assert lines == lines_expected
#
#     @staticmethod
#     def test_constraint_insert_patch_lines_location_basic_with_prior_invariant():
#         """Test patch_line on locations, without creating a new invariant."""
#         lines = [
#             '		<location id="id0" x="0" y="0">\n',
#             '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>\n',
#             "		</location>\n",
#         ]
#
#         lines_expected = [
#             '		<location id="id0" x="0" y="0">\n',
#             '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5 &amp;&amp; c == 3</label>\n',
#             "		</location>\n",
#         ]
#
#         c = ClockConstraintExpression(["c"], "=", 3, True)
#         ci = ConstraintInsert(c)
#         ci.patch_line(lines, 1, 0)
#
#         assert lines == lines_expected
#
#     @staticmethod
#     def test_constraint_insert_patch_lines_transition():
#         """Test patch_line on transitions."""
#         lines = [
#             "		<transition>\n",
#             '			<source ref="id0"/>\n',
#             '			<source ref="id1"/>\n',
#             "		</transition>\n",
#         ]
#
#         lines_expected = [
#             "		<transition>\n",
#             '			<source ref="id0"/>\n',
#             '			<source ref="id1"/>\n',
#             '			<label kind="guard" x="18" y="-34">clock == 5</label>\n',
#             "		</transition>\n",
#         ]
#
#         c = ClockConstraintExpression(["clock"], "=", 5, True)
#         guard = ConstraintLabel("guard", "", (18, -34), [c])
#         ci = ConstraintInsert(c, guard)
#         ci.patch_line(lines, 2, 0)
#
#         assert lines == lines_expected
#
#         lines = [
#             "		<transition>\n",
#             '			<source ref="id0"/>\n',
#             '			<source ref="id1"/>\n',
#             '			<label kind="guard" x="18" y="-34">clock2 == 5</label>\n',
#             '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
#             "		</transition>\n",
#         ]
#
#         lines_expected = [
#             "		<transition>\n",
#             '			<source ref="id0"/>\n',
#             '			<source ref="id1"/>\n',
#             '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; clock == 5</label>\n',
#             '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
#             "		</transition>\n",
#         ]
#
#         c = ClockConstraintExpression(["clock"], "=", 5, True)
#         ci = ConstraintInsert(c)
#         ci.patch_line(lines, 3, 0)
#
#         assert lines == lines_expected
#
#
# class TestConstraintUpdate:
#     """Unit tests for ConstraintUpdate."""
#
#     @staticmethod
#     def test_constraint_update_init():
#         """Test ConstraintUpdate()."""
#         c = ClockConstraintExpression(["x"], ">", 10, False)
#         cu = ConstraintUpdate(c, 13)
#
#         assert cu.constraint == c
#         assert cu.old == 10
#         assert cu.new == 13
#
#     @staticmethod
#     def test_constraint_update_find_matching_constraint():
#         """Test _find_matching_constraint method."""
#         c = ClockConstraintExpression(["x"], ">", 10, False)
#         cu = ConstraintUpdate(c, 13)
#
#         constraints1 = ["x &gt; 10"]
#         constraints2 = ["x == 10", "x &gt; 10"]
#         constraints3 = ["x &gt; 13"]
#
#         assert cu._find_matching_constraint(constraints1) == 0
#         assert cu._find_matching_constraint(constraints2) == 1
#         with pytest.raises(Exception):
#             assert cu._find_matching_constraint(constraints3)
#
#     @staticmethod
#     def test_constraint_update_patch_line_location():
#         """Test patch_line method on locations."""
#         lines = [
#             '		<location id="id0" x="0" y="0">\n',
#             '			<label kind="invariant" x="18" y="-34">x &lt; 5 &amp;&amp; y &lt; 5</label>\n',
#             "		</location>\n",
#         ]
#
#         lines_expected = [
#             '		<location id="id0" x="0" y="0">\n',
#             '			<label kind="invariant" x="18" y="-34">x &lt; 10 &amp;&amp; y &lt; 5</label>\n',
#             "		</location>\n",
#         ]
#
#         c = ClockConstraintExpression(["x"], "<", 5, False)
#         cu = ConstraintUpdate(c, 10)  # Replace threshold 5 with 10.
#         cu.patch_line(lines, 1)
#
#         assert lines == lines_expected
