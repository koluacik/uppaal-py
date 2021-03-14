"""Unit test helpers."""
import os

testcase_dir = "lib/uppaalpy/classes/class_tests/"


def list_xml_in_dir(directory):
    """Return list of xml files in dir."""
    return [
        directory.strip("/") + "/" + x
        for x in os.listdir(directory)
        if x.endswith(".xml")
    ]
