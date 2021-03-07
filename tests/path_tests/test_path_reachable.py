import pytest
from tests.helpers import *

@pytest.mark.parametrize("fp", reachable_nta())
def test_reachable_nta(fp):
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_realizable(path, True)[0] == True

@pytest.mark.parametrize("fp", not_reachable_nta())
def test_not_reachable(fp):
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_realizable(path)[0] == False
