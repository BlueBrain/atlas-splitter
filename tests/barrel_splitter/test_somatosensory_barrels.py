import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import numpy.testing as npt
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

new_ids = {
    "C2": 2000,
    "C2_layers": {
        "1": 2001,
        "2/3": 2004,
        "2": 2002,
        "3": 2003,
        "4": 2005,
        "5": 2006,
        "6a": 2007,
        "6b": 2008,
    },
    "C1": 2010,
    "C1_layers": {
        "1": 2011,
        "2/3": 2014,
        "2": 2012,
        "3": 2013,
        "4": 2015,
        "5": 2016,
        "6a": 2017,
        "6b": 2018,
    },
}


def test_layer_ids():
    id_generator = iter(range(100))
    names = ["region1", "region2", "region3"]
    layers = ["layer1", "layer2"]

    expected_result = {
        0: {"name": "region1", "layers": {"layer1": 1, "layer2": 2}},
        3: {"name": "region2", "layers": {"layer1": 4, "layer2": 5}},
        6: {"name": "region3", "layers": {"layer1": 7, "layer2": 8}},
    }

    result = tested.layer_ids(id_generator, names, layers)
    assert result == expected_result


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

    # def test_region_logical_and():
    #     positions = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    #     annotation = VoxelData(...)
    #     region_map = RegionMap(...)
    #     result = tested.region_logical_and(positions, region, annotation, region_map)
    #     assert result.shape == annotation.data.shape
    #     assert np.sum(result) > 0

    positions_ = positions[(positions.barrel == "C2")][list("xyz")].values
    annotation_test = VoxelData(raw.copy(), (1.0, 1.0, 1.0))
    region_map = RegionMap.from_dict(hierarchy_test["msg"][0])

    mask = region_logical_and(positions_, "SSp-bfd4", annotation_test, region_map)


def test_region_logical_and():
    hierarchy = get_barrel_cortex_excerpt_edited()
    annotation_test, positions = get_barrel_splitter_input_data()


def test_edit_hierarchy():
    layers = ["1", "2/3", "4", "5", "6a", "6b"]
    hierarchy = get_barrel_cortex_excerpt()
    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    tested.edit_hierarchy(hierarchy, new_ids, region_map, 329, ["C1", "C2"], layers)
    expected_hierarchy = get_barrel_cortex_excerpt_edited()

    assert hierarchy == expected_hierarchy
    ## assertions of children


def test_edit_volume():
    layers = ["1", "2", "3", "4", "5", "6a", "6b"]
    annotation_test, positions = get_barrel_splitter_input_data()
    hierarchy = get_barrel_cortex_excerpt_edited()
    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    tested.edit_volume(annotation_test, region_map, positions, layers, new_ids)

    ## assert if positions from df changed in the volume to new index
    ## assert index belonging to hierarchy?
