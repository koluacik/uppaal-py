"""Test path realizability."""

import pytest
from uppaalpy.path_tests.helpers import *


@pytest.mark.parametrize("fp", reachable_nta())
def test_reachable_path(fp):
    """Test realizable paths."""
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_realizable(path, True)[0] == True


@pytest.mark.parametrize("fp", not_reachable_nta())
def test_not_reachable_path(fp):
    """Test not realizable paths."""
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_realizable(path)[0] == False


@pytest.mark.parametrize("fp", reachable_nta())
def test_reachable_path_with_ge_zero_clocks(fp):
    """Test path realizability for all segments of the path."""
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    # path: l - t - l - t - l... for l:location and t:transition
    for i in range(0, len(path), 2):
        for j in range(0, i, 2):
            assert (
                p.path_realizable_with_initial_valuation(
                    path[j:i+1], True, icv_constants={}
                )[0]
                == True
            )
