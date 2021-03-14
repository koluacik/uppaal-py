"""Unit tests for Label class."""
import random
import string

import lxml.etree as ET
import pytest

from uppaalpy import Label

from .helpers import list_xml_in_dir, testcase_dir

label_kinds_list = [
    "synchronisation",
    "assignment",
    "exponentialrate",
    "testcode",
    "testcodeEnter",
    "testcodeExit",
    "select",
]


@pytest.fixture(params=label_kinds_list)
def label_kind(request):
    """Fixture for label kinds."""
    return request.param


def random_label_value():
    """Generate random ascii words."""
    words = []
    for _ in range(random.randint(1, 10)):
        word = []
        for _ in range(random.randint(1, 20)):
            word.append(random.choice(string.ascii_letters))
        words.append("".join(word))
    return " ".join(words)


@pytest.fixture(params=[random_label_value() for _ in range(2)])
def label_value(request):
    """Fixture for label values."""
    return request.param


def random_position():
    """Generate random int pair."""
    return (random.randint(-100, 100), random.randint(-100, 100))


@pytest.fixture(params=[random_position() for _ in range(2)])
def label_position(request):
    """Fixture for label values."""
    return request.param


@pytest.fixture(params=list_xml_in_dir(testcase_dir + "label_xml_files"))
def label_element(request):
    """Fixture for Elements to be converted to Labels."""
    return ET.parse(request.param).getroot()


class TestLabel:
    """Label tests."""

    def test_label_init_no_pos(self, label_kind, label_value):
        """Test Label.__init__.

        Should not throw exceptions.
        """
        Label(label_kind, label_value)

    def test_label_init_with_pos(self, label_kind, label_value, label_position):
        """Test Label.__init__.

        Should not throw exceptions.
        """
        Label(label_kind, label_value, label_position)

    def test_label_from_element(self, label_element):
        """Test Label.from_element."""
        my_label = Label.from_element(label_element)
        assert my_label.kind == label_element.get("kind")
        assert str(my_label.pos[0]) == label_element.get("x")
        assert str(my_label.pos[1]) == label_element.get("y")
        assert my_label.value == label_element.text

    def test_label_to_element(self, label_element):
        """Test Label.to_element."""
        my_label = Label.from_element(label_element)
        my_element = my_label.to_element()
        assert my_element.get("kind") == label_element.get("kind")
        assert my_element.get("x") == label_element.get("x")
        assert my_element.get("y") == label_element.get("y")
        assert my_element.text == label_element.text
