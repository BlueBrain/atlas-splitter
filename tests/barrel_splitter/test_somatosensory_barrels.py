from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import pytest
from voxcell import RegionMap, VoxelData

import atlas_splitter.barrel_splitter.somatosensory_barrels as tested
from tests.barrel_splitter.utils import (
    get_barrel_cortex_excerpt,
    get_barrel_cortex_excerpt_edited,
    get_barrel_splitter_input_data,
)

TEST_PATH = Path(__file__).parent

NEW_IDS = {
    "C1": {
        "C1": 2010,
        "1": 2011,
        "2/3": 2014,
        "2": 2012,
        "3": 2013,
        "4": 2015,
        "5": 2016,
        "6a": 2017,
        "6b": 2018,
    },
    "C2": {
        "C2": 2000,
        "1": 2001,
        "2/3": 2004,
        "2": 2002,
        "3": 2003,
        "4": 2005,
        "5": 2006,
        "6a": 2007,
        "6b": 2008,
    },
}


def test_layer_ids(region_map):
    region = "my-region"
    names = ["region1", "region2", "region3"]
    layers = ["layer1", "layer2"]
    result = tested.layer_ids(region, names, layers, region_map)

    expected = {
        "region1": {"region1": 3100903567, "layer1": 3343828692, "layer2": 2819474802},
        "region2": {"region2": 2741980671, "layer1": 3212473027, "layer2": 1147204648},
        "region3": {"region3": 3227521405, "layer1": 3371952578, "layer2": 1691103868},
    }
    assert result == expected


def test_positions_to_mask():
    positions = np.array([[1, 2, 3], [4, 5, 6]])

    shape = (10, 10, 10)
    annotation = VoxelData(np.zeros(shape), (1.0, 1.0, 1.0))

    result = tested.positions_to_mask(positions, annotation)

    assert result.shape == shape

    assert result[1, 2, 3] == True
    assert result[4, 5, 6] == True


@pytest.fixture
def parent_structure() -> Dict[str, Any]:
    """
    A fixture that returns a parent structure for testing.
    """
    return {
        "id": 1,
        "name": "Parent Structure",
        "acronym": "PST",
        "st_level": 0,
        "graph_order": 0,
        "children": [],
    }


def test_add_hierarchy_child(parent_structure: Dict[str, Any]):
    child_id = 2
    child_name = "Child Structure"
    child_acronym = "CST"

    result = tested.add_hierarchy_child(parent_structure, child_id, child_name, child_acronym)

    assert result["id"] == child_id
    assert result["name"] == child_name
    assert result["acronym"] == child_acronym
    assert result["st_level"] == parent_structure["st_level"] + 1
    assert result["graph_order"] == parent_structure["graph_order"] + 1
    assert len(result["children"]) == 0

    assert parent_structure["id"] == 1
    assert parent_structure["name"] == "Parent Structure"
    assert parent_structure["acronym"] == "PST"
    assert parent_structure["st_level"] == 0
    assert parent_structure["graph_order"] == 0
    assert len(parent_structure["children"]) == 0


def test_region_logical_and():
    raw = np.zeros((3, 57, 57), dtype=int)
    raw[1, 20:30, :] = 1047

    positions_barrel = pd.DataFrame(
        {
            "x": np.ones(57),
            "y": np.arange(0, 57),
            "z": np.ones(57) * 10,
        }
    )

    annotation = VoxelData(raw.copy(), (1.0, 1.0, 1.0))
    annotation = VoxelData(raw.copy(), (1.0, 1.0, 1.0))
    test = np.array(
        np.where(tested.region_logical_and(positions_barrel.values, annotation, [1047]))
    )

    expected = np.array([np.ones(10), np.arange(20, 30), np.ones(10) * 10])
    assert np.all(test == expected)


def test_get_hierarchy_by_acronym():
    hierarchy = get_barrel_cortex_excerpt()
    region_map_test = RegionMap.from_dict(hierarchy["msg"][0])

    hierarchy_test = tested.get_hierarchy_by_acronym(
        hierarchy, region_map_test, start_acronym="SSp-bfd"
    )

    assert hierarchy_test == hierarchy["msg"][0]["children"][0]


def test_edit_hierarchy(region_map):
    layers = ["1", "2/3", "4", "5", "6a", "6b"]
    hierarchy = get_barrel_cortex_excerpt()
    expected_hierarchy = get_barrel_cortex_excerpt_edited()
    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    region = "SSp-bfd"
    # tested.edit_hierarchy(hierarchy, NEW_IDS, region_map, 329, layers)
    tested.edit_hierarchy(region, hierarchy, NEW_IDS, region_map, layers)
    region_map_test = RegionMap.from_dict(hierarchy["msg"][0])

    assert hierarchy == expected_hierarchy

    bc_hierarchy = hierarchy["msg"][0]["children"][0]

    assert np.size(bc_hierarchy["children"]) == 8  # barrel cortex children
    assert np.size(bc_hierarchy["children"][-1]["children"]) == 6  # barrel children
    assert (
        np.size(bc_hierarchy["children"][-1]["children"][1]["children"]) == 2
    )  # barrel layer 2/3 children

    assert region_map_test.get(2001, attr="acronym", with_ascendants=True) == [
        "SSp-bfd-C2-1",
        "SSp-bfd-C2",
        "SSp-bfd",
        "Isocortex",
    ]

    assert list(region_map_test.find("@.*3[ab]?$", attr="acronym")) == [
        201,  # SSp-bfd2/3
        1999,  # SSp-bfd3
        2003,  # SSp-bfd-C2-3
        2004,  # SSp-bfd-C2-2/3
        2013,  # SSp-bfd-C1-3
        2014,  # SSp-bfd-C1-2/3
    ]


@pytest.mark.parametrize(
    "region,layer,sublayer, expected",
    [
        ("SSp-bfd3", None, None, "SSp-bfd3"),
        ("SSp-bfd", "C2", None, "SSp-bfd-C2"),
        ("SSp-bfd", "C2", 3, "SSp-bfd-C2-3"),
    ],
)
def test_acronym(region, layer, sublayer, expected):
    res = tested._acronym(region, layer, sublayer)
    assert res == expected


def test_acronym__raises():
    with pytest.raises(AssertionError):
        tested._acronym("SSp-bfd", None, "foo")


def test_edit_volume():
    layers = ["1", "2", "3", "4", "5", "6a", "6b"]
    annotation_test, positions = get_barrel_splitter_input_data()
    hierarchy = get_barrel_cortex_excerpt_edited()
    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    tested.edit_volume(annotation_test, region_map, positions, layers, NEW_IDS)
    test = annotation_test.raw
    assert test.shape == (3, 57, 57)
    assert np.all(test[0, :, :] == 0)
    assert np.all(test[2, :, :] == 0)

    assert np.all(test[1, 0:5, 10] == 2001)  # C2-layer 1
    assert np.all(test[1, 5:10, 10] == 2002)  # C2-layer 2
    assert np.all(test[1, 10:20, 10] == 2003)  # C2-layer 3
    assert np.all(test[1, 20:30, 10] == 2005)  # C2-layer 4
    assert np.all(test[1, 30:40, 10] == 2006)  # C2-layer 5
    assert np.all(test[1, 40:50, 10] == 2007)  # C2-layer 6a
    assert np.all(test[1, 50:, 10] == 2008)  # C2-layer 6b

    assert np.all(test[1, 0:5, 20] == 2011)  # C1-layer 1
    assert np.all(test[1, 5:10, 20] == 2012)  # C1-layer 2
    assert np.all(test[1, 10:20, 20] == 2013)  # C1-layer 3
    assert np.all(test[1, 20:30, 20] == 2015)  # C1-layer 4
    assert np.all(test[1, 30:40, 20] == 2016)  # C1-layer 5
    assert np.all(test[1, 40:50, 20] == 2017)  # C1-layer 6a
    assert np.all(test[1, 50:, 20] == 2018)  # C1-layer 6b

    assert np.all(test[1, 0:5, 0:10] == 981)  # non-barrel layer 1
    assert np.all(test[1, 5:10, 0:10] == 1998)  # non-barrel layer 2
    assert np.all(test[1, 10:20, 0:10] == 1999)  # non-barrel layer 3
    assert np.all(test[1, 20:30, 0:10] == 1047)  # non-barrel layer 4
    assert np.all(test[1, 30:40, 0:10] == 1070)  # non-barrel layer 5
    assert np.all(test[1, 40:50, 0:10] == 1038)  # non-barrel layer 6a
    assert np.all(test[1, 50:, 0:10] == 1062)  # non-barrel layer 6b
