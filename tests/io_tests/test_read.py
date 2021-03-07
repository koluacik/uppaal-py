import pytest
from tests.helpers import *
import lxml.etree as ET

@pytest.mark.parametrize("fp", broken_xml())
def test_bad_xml(fp):
    with pytest.raises(ET.XMLSyntaxError):
        assert read_file(fp)

@pytest.mark.parametrize("fp", broken_nta())
def test_bad_nta(fp):
    with pytest.raises(Exception):
        assert read_file(fp)

@pytest.mark.parametrize("fp", good_nta() + generator_ntas())
def test_good_nta(fp):
    read_file(fp)
