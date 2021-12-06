"""Unit tests for split_23"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest
from voxcell import RegionMap

import atlas_splitter.layer_splitter.isocortex_layer_23 as tested
from atlas_splitter.exceptions import AtlasSplitterError
from tests.layer_splitter.utils import get_splitting_input_data

TEST_PATH = Path(__file__).parent.parent


def get_isocortex_hierarchy_excerpt():
    return {
        "id": 315,
        "acronym": "Isocortex",
        "name": "Isocortex",
        "children": [
            {
                "id": 500,
                "acronym": "MO",
                "name": "Somatomotor areas",
                "children": [
                    {
                        "id": 107,
                        "acronym": "MO1",
                        "name": "Somatomotor areas, Layer 1",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                    {
                        "id": 218,
                        "acronym": "MO2",
                        "name": "Somatomotor areas, Layer 2",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                    {
                        "id": 219,
                        "acronym": "MO2/3",
                        "name": "Somatomotor areas, Layer 2/3",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                    {
                        "id": 299,
                        "acronym": "MO5",
                        "name": "Somatomotor areas, Layer 5",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                    {
                        "id": 644,
                        "acronym": "MO6a",
                        "name": "Somatomotor areas, Layer 6a",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                    {
                        "id": 947,
                        "acronym": "MO6b",
                        "name": "Somatomotor areas, Layer 6b",
                        "children": [],
                        "parent_structure_id": 500,
                    },
                ],
                "parent_structure_id": 315,
            }
        ],
    }


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


def test_edit_hierarchy():
    isocortex_hierarchy = get_isocortex_hierarchy_excerpt()
    expected_hierarchy = get_isocortex_hierarchy_excerpt()
    # Removes "Somatomotor areas, Layer 2"
    # The corresponding identifier should be reused
    del expected_hierarchy["children"][0]["children"][1]

    expected_hierarchy["children"][0]["children"][1]["children"] = [
        {
            "id": 218,
            "acronym": "MO2",
            "name": "Somatomotor areas, Layer 2",
            "children": [],
            "parent_structure_id": 219,
        },
        {
            "id": 948,
            "acronym": "MO3",
            "name": "Somatomotor areas, Layer 3",
            "children": [],
            "parent_structure_id": 219,
        },
    ]
    new_layer_ids = defaultdict(dict)
    ids_to_reuse = defaultdict(dict)
    region_map = RegionMap.from_dict(
        {"acronym": "root", "name": "root", "id": 0, "children": [isocortex_hierarchy]}
    )
    tested.edit_hierarchy(
        isocortex_hierarchy,
        new_layer_ids,
        ids_to_reuse,
        region_map,
        tested.create_id_generator(region_map),
    )

    assert isocortex_hierarchy == expected_hierarchy


def test_edit_hierarchy_full_json_file():
    region_map = RegionMap.load_json(str(Path(TEST_PATH, "1.json")))
    isocortex_ids = region_map.find("Isocortex", attr="acronym", with_descendants=True)
    assert not isocortex_ids & (
        region_map.find("@.*3[ab]?$", attr="acronym") - region_map.find("@.*2/3$", attr="acronym")
    )
    # As of 2020.04.22, AIBS's Isocortex has 4 region ids in layer 2 but none in layer 3.
    # initial_isocortex_layer_2_ids = isocortex_ids & region_map.find("@.*2$", attr="acronym")  # 4 ids, see below
    isocortex_layer_23_ids = isocortex_ids & region_map.find("@.*2/3$", attr="acronym")
    isocortex_hierarchy = None
    new_layer_ids = defaultdict(dict)
    ids_to_reuse = defaultdict(dict)
    with open(str(Path(TEST_PATH, "1.json")), encoding="utf-8") as h_file:
        allen_hierarchy = json.load(h_file)
        isocortex_hierarchy = tested.get_isocortex_hierarchy(allen_hierarchy)
    tested.edit_hierarchy(
        isocortex_hierarchy,
        new_layer_ids,
        ids_to_reuse,
        region_map,
        tested.create_id_generator(region_map),
    )
    assert ids_to_reuse == {
        304: {"layer_2": 195},
        556: {"layer_2": 747},
        582: {"layer_2": 524},
        430: {"layer_2": 606},
    }

    modified_region_map = RegionMap.from_dict(isocortex_hierarchy)
    assert modified_region_map.find("@.*2/3$", attr="acronym") == isocortex_layer_23_ids
    isocortex_layer_2_ids = modified_region_map.find("@.*2$", attr="acronym")
    isocortex_layer_3_ids = modified_region_map.find("@.*[^/]3$", attr="acronym")
    assert len(isocortex_layer_2_ids) == len(isocortex_layer_23_ids)
    assert len(isocortex_layer_3_ids) == len(isocortex_layer_23_ids)


def test_split_isocortex_layer_23():
    allen_hierarchy = None
    with open(str(Path(TEST_PATH, "1.json")), encoding="utf-8") as h_file:
        allen_hierarchy = json.load(h_file)

    data = get_splitting_input_data()
    tested.split(allen_hierarchy, data["annotation"], data["direction_vectors"], data["ratio"])
    isocortex_hierarchy = tested.get_isocortex_hierarchy(allen_hierarchy)
    modified_region_map = RegionMap.from_dict(isocortex_hierarchy)
    isocortex_layer_2_ids = modified_region_map.find("@.*2$", attr="acronym")
    isocortex_layer_3_ids = modified_region_map.find("@.*[^/]3$", attr="acronym")
    assert len(modified_region_map.find("@.*2/3$", attr="acronym")) == len(isocortex_layer_3_ids)
    npt.assert_array_equal(
        np.unique(data["annotation"].raw),
        sorted({0} | isocortex_layer_2_ids | isocortex_layer_3_ids),
    )
    layer_2_mask = np.isin(data["annotation"].raw, list(isocortex_layer_2_ids))
    layer_3_mask = np.isin(data["annotation"].raw, list(isocortex_layer_3_ids))
    npt.assert_array_equal(data["annotation"].raw > 0, np.logical_or(layer_2_mask, layer_3_mask))

    layer_2_indices = np.where(np.isin(data["annotation"].raw, list(isocortex_layer_2_ids)))
    layer_3_indices = np.where(np.isin(data["annotation"].raw, list(isocortex_layer_3_ids)))
    assert np.count_nonzero(layer_2_indices[1] > data["layer_3_top"]) >= 0.95 * len(
        layer_2_indices[1]
    )
    assert np.count_nonzero(layer_3_indices[1] <= data["layer_3_top"]) >= 0.95 * len(
        layer_3_indices[1]
    )


def test_split_isocortex_layer_23_exception():
    allen_hierarchy = None
    with open(str(Path(TEST_PATH, "1.json")), encoding="utf-8") as h_file:
        allen_hierarchy = json.load(h_file)

    data = get_splitting_input_data()
    data["direction_vectors"][1, 25, 25] = [np.nan] * 3

    with pytest.raises(AtlasSplitterError, match=".*\\[NaN, NaN, NaN\\] direction vector.*"):
        tested.split(allen_hierarchy, data["annotation"], data["direction_vectors"], data["ratio"])
