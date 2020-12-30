import pytest
import uppaalpy
import xml.etree.cElementTree as ET
from tests.helpers import *

@pytest.mark.parametrize("fp", good_nta() + generator_ntas())
def test_write(fp):
    write_to_file(read_file(fp))

@pytest.mark.parametrize("fp", good_nta() + generator_ntas())
def test_write_p(fp):
    write_to_file_pretty(read_file(fp))
