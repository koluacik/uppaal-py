"""Test path concatenation."""

import pytest

from uppaalpy.path_analysis import concatenate_paths
from uppaalpy.path_tests.helpers import *


def get_test_data(path):
    nta = read_file(path)
    p1, p2, template, res = get_path_concatenation_test(nta)
    return p1, p2, template, res


@pytest.mark.parametrize("fp", concatenation_tests())
def test_path_concatenation_0(fp):
    p1, p2, t, res = get_test_data(fp)
    paths = concatenate_paths(t, p1, p2)
    assert len(paths) == res
    for p in paths:
        assert len(p) == len(p1) + len(p2) + 1
