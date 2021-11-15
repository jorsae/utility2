import pytest
import os
import sys
sys.path.append('.')
import renamer

@pytest.mark.parametrize("path, expected", [
    ('.', os.getcwd()),
    ('C:', 'C:\\'),
    ('C:\\ProgramData', 'C:\\ProgramData'),
    ('test\\test_renamer.py', 'D:\\Code\\utility\\test\\test_renamer.py'),
])

def test_get_path(path, expected):
    assert(renamer.get_path(path)) == expected