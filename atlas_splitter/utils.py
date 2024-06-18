"""Utilities for splitting atlases."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict

from voxcell import RegionMap, VoxcellError

from atlas_splitter.exceptions import AtlasSplitterError

L = logging.getLogger(__name__)

HierarchyDict = Dict[str, Any]

MIN_CUSTOM_ID = 20_000
MAX_CUSTOM_ID = 30_000


def get_isocortex_hierarchy(allen_hierachy: HierarchyDict):
    """
    Extract the hierarchy dict of the iscortex from AIBS hierarchy dict.
    Args:
        allen_hierarchy: AIBS hierarchy dict instantiated from
            http://api.brain-map.org/api/v2/structure_graph_download/1.json.
    """
    error_msg = "Wrong input. The AIBS 1.json file is expected."
    if "msg" not in allen_hierachy:
        raise AtlasSplitterError(error_msg)

    hierarchy = allen_hierachy["msg"][0]
    try:
        while hierarchy["acronym"] != "Isocortex":
            hierarchy = hierarchy["children"][0]
    except KeyError as error:
        raise AtlasSplitterError(error_msg) from error

    return hierarchy


def id_from_acronym(region_map: RegionMap, acronym: str, extra_ids: None | set = None) -> int:
    """Create an identifier from the input acronym.

    Args:
        region_map: map to navigate the brain region hierarchy.
        acronym: str for the region acronym
        extra_ids: a set of IDs that should also be checked for collision

    Return:
        region id.

    Raises Exception if the hashed acronym ID already exists
    """
    if extra_ids is None:
        extra_ids = set()

    region_id_set = region_map.find(acronym, attr="acronym", with_descendants=False)
    if region_id_set:
        return next(iter(region_id_set))

    # acronym not present in hierarchy, generating a corresponding id
    region_id = _hash_derived_id(acronym)

    if region_id in extra_ids:
        raise RuntimeError("generated ID exists in extra_ids")

    try:
        acronym = region_map.get(region_id, "acronym")
    except VoxcellError:
        L.info("Creating new id %s for acronym '%s'", region_id, acronym)
        return region_id

    raise RuntimeError(f"Found a collision with acronym '{acronym}'")


def _hash_derived_id(acronym: str) -> int:
    """Create an id from the acronym's sha256 digest.

    Notes:
        The id is generated in the [MIN_CUSTOM_ID, MAX_CUSTOM_ID] interval for two reasons:
            - Be outside the current ids range
            - Fit within the range of int16
    """
    sha = hashlib.sha256(acronym.encode("utf-8"))
    integer = int.from_bytes(sha.digest(), "big")
    return MIN_CUSTOM_ID + integer % (MAX_CUSTOM_ID - MIN_CUSTOM_ID)


def _assert_is_leaf_node(node) -> None:
    """
    Raises an AtalasSplitterError if `node` is not a leaf node.

    Args:
        node: node of the hierarchy tree. Dict of the form
        {
            "id": 195,
                   "atlas_id": 1014,
                   "ontology_id": 1,
                   "acronym": "PL2",
                   "name": "Prelimbic area, layer 2",
                   "color_hex_triplet": "2FA850",
                   "graph_order": 240,
                   "st_level": 11,
                   "hemisphere_id": 3,
                   "parent_structure_id": 972,
                   "children": []
                  },

        }
    Raises:
        AtlasSplitterError if `node` is a not a leaf `node`.
    """
    if "children" not in node:
        raise AtlasSplitterError(f'Missing "children" key for region {node["name"]}.')
    if node["children"] != []:
        raise AtlasSplitterError(
            f'Region {node["name"]} has an unexpected "children" value: '
            f'{node["children"]}. Expected: [].'
        )
