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

@pytest.mark.parametrize("filter, files, expected", [
    (['*'], ['a.txt', 'b.jpg', 'c.mp4', ''], [True, True, True, True]),
    (['.txt'], ['a.txt', 'b.txt.jpg', 'c.txt.txt', ''], [True, False, True, False]),
    (['.jpg'], ['a.txt', 'b.jpg', 'c.jpg.txt', ''], [False, True, False, False]),
])
def test_check_extension(filter, files, expected):
    index = 0
    for file in files:
        matches = renamer.check_extension(file, filter)
        assert(matches) == expected[index]
        index += 1