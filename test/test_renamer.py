import pytest
import os
import sys
sys.path.append('.')
import r

@pytest.mark.parametrize("path, expected", [
    ('.', os.getcwd()),
    ('C:', 'C:\\'),
    ('C:\\ProgramData', 'C:\\ProgramData'),
])

def test_get_path(path, expected):
    assert(r.get_path(path)) == expected