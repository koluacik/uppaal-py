import pytest
from tests.helpers import *

@pytest.mark.parametrize("fp", good_nta() + generator_ntas())
def test_write(fp):
    write_to_file(read_file(fp))
