"""Unit tests for ConstraintChange and its subclasses."""

import pytest
from pytest_cases.case_parametrizer_new import parametrize_with_cases

from uppaalpy.classes.class_tests.test_constraint_change_cases import (
    CaseCRInit,
    CaseIPatch,
    CaseIinit,
    CaseRFind,
    CaseRPatch,
    CaseUFind,
    CaseUInit,
    CaseUPatch,
)
from uppaalpy.classes.constraint_patcher import (
    ConstraintInsert,
    ConstraintRemove,
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


class TestConstraintInsert:
    """Unit tests for ConstraintInsert."""

    @parametrize_with_cases("obj, new_label", cases=CaseIinit)
    def test_constraint_insert_init(self, obj, new_label):
        """Test ConstraintInsert()."""
        ci = ConstraintInsert(obj, new_label)
        assert ci.constraint == obj

    @parametrize_with_cases("ci, lines, res, i, pi", cases=CaseIPatch)
    def test_patch(self, ci, lines, res, i, pi):
        ci.patch_line(lines, i, pi)
        assert len(lines) == len(res)
        for l, r in zip(lines, res):
            assert l == r

class TestConstraintUpdate:
    """Unit tests for ConstraintUpdate."""

    @parametrize_with_cases("c, update, old, new", cases=CaseUInit)
    def test_constraint_update_init(self, c, update, old, new):
        """Test ConstraintUpdate()."""

        assert update.constraint == c
        assert update.old == old
        assert update.new == new

    @parametrize_with_cases("cu, exprs, res", cases=CaseUFind)
    def test_constraint_update_find(self, cu, exprs, res):
        if res is not None:
            assert cu._find_matching_constraint(exprs) == res
        else:
            with pytest.raises(Exception):
                assert cu._find_matching_constraint(exprs)


    @parametrize_with_cases("cu, lines, index, res", cases=CaseUPatch)
    def test_constraint_update_patch(self, cu, lines, index, res):
        cu.patch_line(lines, index)
        assert lines == res
