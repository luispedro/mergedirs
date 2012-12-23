import os
import merge
def test_hash_file():
    h = merge.hash_file('tests/data/A/3')
    h2 = merge.hash_file('tests/data/A/3')
    assert h == h2
    assert type(h) is str

def test_props_for():
    p = merge.props_for('tests/data/A/3')
    p2 = merge.props_for('tests/data/A/3')
    assert p == p2
    p2 = merge.props_for('tests/data/B/3')
    assert p != p2

def test_rsync_copy():
    p = merge.props_for('tests/data/A/1')
    p2 = merge.props_for('tests/data/B/1')
    assert p == p2

def test_merge():
    options,_ = merge.parse_options(['merge'])
    for op, args in merge.merge('tests/data/A', 'tests/data/B', options):
        assert op in (os.rename, os.unlink)
