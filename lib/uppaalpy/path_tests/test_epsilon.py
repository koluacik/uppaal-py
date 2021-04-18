"""Check the behavior of the path analysis on open/closed NTA."""
import pytest
from uppaalpy.path_tests.helpers import *

@pytest.mark.parametrize("fp", epsilon_tests())
def test_epsilon(fp):
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_realizable(path, add_epsilon=False)[0] \
            and not p.path_realizable(path, add_epsilon=True)[0]
