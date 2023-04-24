"""Unit tests for utils"""
import json
from pathlib import Path

import numpy.testing as npt
import pytest
from voxcell import RegionMap

import atlas_splitter.utils as tested
from atlas_splitter.exceptions import AtlasSplitterError

TEST_PATH = Path(__file__).parent


def test_get_isocortex_hierarchy():
    with pytest.raises(AtlasSplitterError):
        allen_hierarchy = {
            "root": [
                {
                    "id": 998,
                    "children": [
                        {
                            "id": 0,
                            "acronym": "grey matter",
                            "children": [{"id": 1, "acronym": "End of the world"}],
                        }
                    ],
                }
            ]
        }
        tested.get_isocortex_hierarchy(allen_hierarchy)
    with pytest.raises(AtlasSplitterError):
        allen_hierarchy = {
            "msg": [
                {
                    "id": 998,
                    "children": [
                        {
                            "id": 0,
                            "acronym": "root",
                            "children": [{"id": 1, "acronym": "End of the world"}],
                        }
                    ],
                }
            ]
        }
        tested.get_isocortex_hierarchy(allen_hierarchy)


def test_get_isocortex_hierarchy_exception():
    with open(str(Path(TEST_PATH, "1.json", encoding="utf-8"))) as h_file:
        allen_hierarchy = json.load(h_file)
        isocortex_hierarchy = tested.get_isocortex_hierarchy(allen_hierarchy)
        assert isocortex_hierarchy["acronym"] == "Isocortex"


def test_create_id_generator():
    region_map = RegionMap.load_json(str(Path(TEST_PATH, "1.json", encoding="utf-8")))
    id_generator = tested.create_id_generator(region_map)

    npt.assert_array_equal(
        (
            next(id_generator),
            next(id_generator),
            next(id_generator),
        ),
        (614454278, 614454279, 614454280),
    )
