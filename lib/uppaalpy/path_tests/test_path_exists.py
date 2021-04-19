"""Tests for path existance check logic."""
import pytest
from uppaalpy.path_tests.helpers import *

@pytest.mark.parametrize("fp", path_exists())
def test_path_exists(fp):
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert p.path_exists(path)

@pytest.mark.parametrize("fp", path_not_exists())
def test_path_not_exists(fp):
    nta = read_file(fp)
    path = get_path_from_query_comment(nta)
    assert not p.path_exists(path)
