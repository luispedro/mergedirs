import os
import merge
def test_hash_file():
    h = merge.hash_file('merge/tests/data/A/3')
    h2 = merge.hash_file('merge/tests/data/A/3')
    assert h == h2

def test_props_for():
    p = merge.props_for('merge/tests/data/A/3')
    p2 = merge.props_for('merge/tests/data/A/3')
    assert p == p2
    p2 = merge.props_for('merge/tests/data/B/3')
    assert p != p2

def test_rsync_copy():
    p = merge.props_for('merge/tests/data/A/1')
    p2 = merge.props_for('merge/tests/data/B/1')

    assert p[:3] == p2[:3]
    # Rsync does not always copy the full timestamp, but it should copy the
    # integer version:
    assert int(p[3]) == int(p2[3])

def test_merge_actions():
    options,_ = merge.parse_options(['merge'])
    n = 0
    for op in merge.mergedirs('merge/tests/data/A', 'merge/tests/data/B', options):
        n += 1
        assert op.f in (os.rename, os.unlink)
    assert n > 0
