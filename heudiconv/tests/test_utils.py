import json
import os
import os.path as op

from heudiconv.utils import (
    get_known_heuristics_with_descriptions,
    get_heuristic_description,
    load_heuristic,
    json_dumps_pretty,
    load_json,
    create_tree,
    save_json,
    JSONDecodeError)

import pytest
from .utils import HEURISTICS_PATH


def test_get_known_heuristics_with_descriptions():
    d = get_known_heuristics_with_descriptions()
    assert {'reproin', 'convertall'}.issubset(d)
    # ATM we include all, not only those two
    assert len(d) > 2
    assert len(d['reproin']) > 50  # it has a good one
    assert len(d['reproin'].split(os.sep)) == 1  # but just one line


def test_get_heuristic_description():
    desc = get_heuristic_description('reproin', full=True)
    assert len(desc) > 1000
    # and we describe such details as
    assert '_ses-' in desc
    assert '_run-' in desc
    # and mention ReproNim ;)
    assert 'ReproNim' in desc


def test_load_heuristic():
    by_name = load_heuristic('reproin')
    from_file = load_heuristic(op.join(HEURISTICS_PATH, 'reproin.py'))

    assert by_name
    assert by_name.filename == from_file.filename

    with pytest.raises(ImportError):
        load_heuristic('unknownsomething')

    with pytest.raises(ImportError):
        load_heuristic(op.join(HEURISTICS_PATH, 'unknownsomething.py'))


def test_json_dumps_pretty():
    pretty = json_dumps_pretty
    assert pretty({"SeriesDescription": "Trace:Nov 13 2017 14-36-14 EST"}) \
        == '{\n  "SeriesDescription": "Trace:Nov 13 2017 14-36-14 EST"\n}'
    assert pretty({}) == "{}"
    assert pretty({"a": -1, "b": "123", "c": [1, 2, 3], "d": ["1.0", "2.0"]}) \
        == '{\n  "a": -1,\n  "b": "123",\n  "c": [1, 2, 3],\n  "d": ["1.0", "2.0"]\n}'
    assert pretty({'a': ["0.3", "-1.9128906358217845e-12", "0.2"]}) \
        == '{\n  "a": ["0.3", "-1.9128906358217845e-12", "0.2"]\n}'
    # original, longer string
    tstr = 'f9a7d4be-a7d7-47d2-9de0-b21e9cd10755||' \
          'Sequence: ve11b/master r/50434d5; ' \
          'Mar  3 2017 10:46:13 by eja'
    # just the date which reveals the issue
    # tstr = 'Mar  3 2017 10:46:13 by eja'
    assert pretty({'WipMemBlock': tstr}) == '{\n  "WipMemBlock": "%s"\n}' % tstr


def test_load_json(tmpdir, caplog):
    # test invalid json
    ifname = 'invalid.json'
    invalid_json_file = str(tmpdir / ifname)
    create_tree(str(tmpdir), {ifname: u"I'm Jason Bourne"})

    with pytest.raises(JSONDecodeError):
        load_json(str(invalid_json_file))

    assert ifname in caplog.text

    # test valid json
    vcontent = {"secret": "spy"}
    vfname = "valid.json"
    valid_json_file = str(tmpdir / vfname)
    save_json(valid_json_file, vcontent)
    
    assert load_json(valid_json_file) == vcontent
