"""Unit tests for Label class."""

from pytest_cases.case_parametrizer_new import parametrize_with_cases

from uppaalpy.classes.class_tests.test_label_cases import (
    CaseLabelFromElement,
    CaseLabelInit,
    CaseLabelToElement,
)
from uppaalpy.classes.simplethings import Label


class TestLabel:
    @parametrize_with_cases("kind, val, pos", cases=CaseLabelInit)
    def test_init(self, kind, val, pos):
        Label(kind, val, pos)

    @parametrize_with_cases("element", cases=CaseLabelFromElement)
    def test_from_element(self, element):
        Label.from_element(element)

    @parametrize_with_cases("element", cases=CaseLabelToElement)
    def test_to_element(self, element):
        e = Label.from_element(element)
        element2 = e.to_element()
        assert element.tag == element2.tag
        assert element.text == element2.text
        assert element.get("x") == element2.get("x")
        assert element.get("y") == element2.get("y")


class TestUpdateLabel:
    pass
