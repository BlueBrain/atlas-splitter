"""Unit tests for utils"""
import json
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest
from voxcell import RegionMap
from voxcell.exceptions import VoxcellError

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


def test_id_from_acronym(region_map):

    # existing region -> existing id
    res1 = tested.id_from_acronym(region_map, "VISp1")
    _assert_within_integer_type_range(res1, np.uint32)
    assert region_map.get(res1, attr="acronym") == "VISp1"

    # new region -> non-existing id
    res2 = tested.id_from_acronym(region_map, "VISPXXX")
    _assert_within_integer_type_range(res2, np.uint32)
    with pytest.raises(VoxcellError, match="Region ID not found"):
        region_map.get(res2, attr="acronym")


def _assert_within_integer_type_range(value, int_dtype):
    info = np.iinfo(int_dtype)
    check = info.min <= value < info.max
    assert check, (
        f"Value not within dtype '{int_dtype.__name__}' range: "
        f"{info.min} <= {value} < {info.max}"
    )


def test_create_id_generator(region_map):
    id_generator = tested.create_id_generator(region_map)

    npt.assert_array_equal(
        (
            next(id_generator),
            next(id_generator),
            next(id_generator),
        ),
        (614454278, 614454279, 614454280),
    )
