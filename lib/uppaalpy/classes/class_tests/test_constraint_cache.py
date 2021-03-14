"""Tests for the ConstraintCache and ConstraintPatch classes.

A complete NTA object is required to test these classes.
"""

from uppaalpy.classes.constraint_patcher import ConstraintPatch, ConstraintUpdate
from .helpers import testcase_dir

from uppaalpy import NTA


class TestConstraintPatch:
    """Unit test for ConstraintPatch."""

    def test_constraint_patch_init_transition(self):
        """Test ConstraintPatch()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First transition
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], 10, 15)

        cp = ConstraintPatch(template, update, transition_ref=transition)

        assert cp.template_ref == template
        assert cp.transition_ref == transition
        assert cp.change == update

    def test_constraint_patch_init_location(self):
        """Test ConstraintPatch()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")

        # Update the invariant of l0 in the first template.
        # x <= 10 -> x <= 15
        template = nta.templates[0]  # First template
        location = template.graph._named_locations["l0"]
        constraints = location.invariant.constraints

        update = ConstraintUpdate(constraints[0], 10, 15)

        cp = ConstraintPatch(template, update, location_ref=location)

        assert cp.template_ref == template
        assert cp.location_ref == location
        assert cp.change == update


class TestConstraintCache:
    """Unit tests for ConstraintCache."""

    def test_constraint_cache_init(self):
        """Test ConstraintCache()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        assert cc.nta == nta
        assert cc.patches == []

    def test_constraint_cache_cache(self):
        """Test ConstraintCache.cache()."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First template
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], 10, 15)

        cp = ConstraintPatch(template, update, transition_ref=transition)
        cc.cache(cp)

        assert cc.patches == [cp]

    def test_constraint_cache_apply_single_patch(self):
        """Test _apply_single_patch method."""
        nta = NTA.from_xml(testcase_dir + "constraint_cache_xml_files/test01.xml")
        cc = nta.patch_cache

        # Update the threshold of the transition in the second template.
        # x <= 10 -> x <= 15
        template = nta.templates[1]  # Second template
        transition = template.graph._transitions[0]  # First template
        constraints = transition.guard.constraints

        update = ConstraintUpdate(constraints[0], 10, 15)

        cp = ConstraintPatch(template, update, transition_ref=transition)
        cc.cache(cp)

        lines = open(testcase_dir + "constraint_cache_xml_files/test01.xml").readlines()
        lines_subject_to_change = lines[:]

        cc._apply_single_patch(lines_subject_to_change, cc.patches[0])

        # 56th line is changed.
        assert lines[:55] == lines_subject_to_change[:55]
        assert lines[56:] == lines_subject_to_change[56:]
        assert lines[55].replace("10", "15") == lines_subject_to_change[55]
