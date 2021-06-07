"""Tests for the ConstraintCache and ConstraintPatch classes.

A complete NTA object is required to test these classes.
"""

from uppaalpy.classes.constraint_patcher import ConstraintPatch, ConstraintUpdate
from uppaalpy.classes.nta import NTA

from .helpers import testcase_dir


class TestConstraintPatch:
    """Unit test for ConstraintPatch."""

    @staticmethod
    def test_constraint_patch_init_transition():
        """Test ConstraintPatch()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First transition
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], 15)  # type: ignore

        cp = ConstraintPatch(template, update, obj_ref=transition)

        assert cp.template_ref == template
        assert cp.obj_ref == transition
        assert cp.change == update

    @staticmethod
    def test_constraint_patch_init_location():
        """Test ConstraintPatch()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")

        # Update the invariant of l0 in the first template.
        # x <= 10 -> x <= 15
        template = nta.templates[0]  # First template
        location = template.graph._named_locations["l0"]
        constraints = location.invariant.constraints

        update = ConstraintUpdate(constraints[0], 15)  # type: ignore

        cp = ConstraintPatch(template, update, obj_ref=location)

        assert cp.template_ref == template
        assert cp.obj_ref == location
        assert cp.change == update


class TestConstraintCache:
    """Unit tests for ConstraintCache."""

    @staticmethod
    def test_constraint_cache_init():
        """Test ConstraintCache()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        assert cc.nta == nta
        assert cc.patches == []

    @staticmethod
    def test_constraint_cache_cache():
        """Test ConstraintCache.cache()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First template
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], 15)  # type: ignore

        cp = ConstraintPatch(template, update, obj_ref=transition)
        cc.cache(cp)

        assert cc.patches == [cp]

    @staticmethod
    def test_constraint_cache_apply_single_patch():
        """Test _apply_single_patch method."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First template
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], "15") # type: ignore

        cp = ConstraintPatch(template, update, obj_ref=transition)
        cc.cache(cp)

        lines = open(testcase_dir + "constraint_cache_xml_files/test01.xml").readlines()
        lines_subject_to_change = lines[:]

        cc._apply_single_patch(lines_subject_to_change, cc.patches[0])

        # 56th line is changed.
        assert lines[:56] == lines_subject_to_change[:56]
        assert lines[57:] == lines_subject_to_change[57:]
        assert lines[56].replace("10", "15") == lines_subject_to_change[56]
