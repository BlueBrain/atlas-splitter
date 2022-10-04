"""
Algorithm 

"""

# ## Add Barrels as children to Layer 4 of Barrel Field
# # Update the Hierarchy to include barrels
# TODO - to close the efforts:
#
# 1. Edit the SSp-bfd4 to have new children of the barrel volumes in the hierarchy
# 2. Edit the brain_regions to include the new hierarchy elements (get indices to have a new id)
#
# Issues / Questions:
#
# 1. How do I get the access to the hierarchy in an elegant way?
# 2. What about other nrrd files updates?
# 3. Plan for updating the brain_regions.nrrd
import copy
import logging
import blueetl
import numpy as np
import pandas as pd
from typing import Any, Dict, Iterator, Set
from itertools import count
from collections import defaultdict
from voxcell import RegionMap, VoxelData
from atlas_commons.typing import NDArray, BoolArray
from atlas_splitter.exceptions import AtlasSplitterError


L = logging.getLogger(__name__)
HierarchyDict = Dict[str, Any]


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


def create_id_generator(region_map: RegionMap) -> Iterator[int]:
    """Create an identifiers generator.

    The generator produces an identifier which is different from all
    the previous ones and from the identifiers in use in `self.region_map`.

    Args:
        region_map: map to navigate the brain region hierarchy.

    Return:
        iterator providing the next id.
    """
    last = max(region_map.find("root", attr="acronym", with_descendants=True))
    return count(start=last + 1)


def change_volume(volume, id_: int, new_id: int, layer_mask) -> None:
    """
    Modify `volume` by a assigining a new identifier to the voxels defined by `layer_mask`.

    The modification is done in place.

    Args:
        id_: the original identifier to be changed.
        new_id: the new identifier to be assigned.
        layer_mask: binary mask of the voxels of the layer where the change is requested.
    """
    change_to_layer = np.logical_and(volume == id_, layer_mask)
    if np.any(change_to_layer):
        volume[change_to_layer] = new_id


def get_hierarchy_by_acronym(hierarchy, acronym):  
    for index, child in enumerate(hierarchy["children"]):
        if child["acronym"] == acronym:
            return hierarchy["children"][index]


def positions_to_mask(positions, mask, orientation) -> BoolArray:
    """_summary_

    Args:
        positions (_type_): _description_
        mask (_type_): _description_
        orientation (_type_): _description_

    Returns:
        _type_: _description_
    """    
    mask = np.zeros_like(mask)
    indices = orientation.positions_to_indices(positions)

    for indx in indices:
        mask[indx[0], indx[1], indx[2]] = True

    return mask


def edit_hierarchy(
    hierarchy: HierarchyDict,
    new_ids: Dict[int, Dict[str, int]],
    region_map: RegionMap,
    start_index: int,
    barrel_names,
) -> None:

    hierarchy_levels = np.array(
        region_map.get(start_index, attr="acronym", with_ascendants=True)
    )
    iso_index = np.where(hierarchy_levels == "Isocortex")[0][0]
    hierarchy_levels = hierarchy_levels[:iso_index]
    hierarchy_ = get_isocortex_hierarchy(hierarchy)

    for acronym in hierarchy_levels[::-1]:
        hierarchy_ = get_hierarchy_by_acronym(hierarchy_, acronym)

    new_children = []
    for name in barrel_names:
        new_child = copy.deepcopy(hierarchy_)
        new_child["parent_structure_id"] = hierarchy_["id"]
        new_child["acronym"] = hierarchy_["acronym"] + f"-{name}"
        new_child["name"] = hierarchy_["name"] + f", {name} barrel"
        new_child["id"] = new_ids[name]
        new_child["st_level"] = hierarchy_["st_level"] + 1
        new_child["graph_order"] = hierarchy_["graph_order"] + 1
        new_children.append(new_child)

    hierarchy_["children"] = new_children


def edit_volume(
    volume: NDArray,
    barrel_positions: pd.DataFrame,
    atlas,
    region: str,
    region_id: int,
    new_ids: Dict[str, int],
):
    mask = atlas.get_region_mask(region).raw
    orientation = atlas.load_data("orientation")

    for name in barrel_positions.barrel.unique():
        positions = barrel_positions.etl.q(barrel=name)[["x", "y", "z"]]
        barrel_mask = positions_to_mask(positions.values, mask, orientation).astype(
            np.uint8
        )
        new_id = new_ids[name]
        change_to_layer = np.logical_and(volume == region_id, barrel_mask)
        volume[change_to_layer] = new_id


def split(
    hierarchy: HierarchyDict,
    annotation: VoxelData,
    barrel_positions: pd.DataFrame,
    atlas,
):
    barrel_names = np.sort(barrel_positions.barrel.unique())
    region_map = RegionMap.from_dict(hierarchy["msg"][0])
    indices = region_map.find("SSp-bfd4", attr="acronym", with_descendants=True)
    ssp_bfd4_index = indices.pop()
    id_generator = create_id_generator(region_map)

    new_ids: Dict[int, Dict[str, int]] = defaultdict(dict)
    for name in barrel_names:
        new_ids[name] = next(id_generator)

    edit_hierarchy(
        hierarchy,
        new_ids,
        region_map,
        start_index=ssp_bfd4_index,
        barrel_names=barrel_names,
    )

    edit_volume(
        annotation, barrel_positions, atlas, "SSp-bfd4", ssp_bfd4_index, new_ids
    )
