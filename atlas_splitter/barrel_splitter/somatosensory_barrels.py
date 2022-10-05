"""
Algorithm introducing volumes of 33 barrels coming from segmentation results of the 
average brain atlas images from Allen institute. Barrels are introduced as children 
to somatosensory area of barrel cortex layer 4. 

* Introduction of barrels to the hierarchy.json
* Introduction of the annotated volues to the brain_regions.nrrd

The code relays on pd.DataFrame contining the annotated positions of each barrel voxel
in x,y,z coordinates.
"""
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


def get_hierarchy_by_acronym(hierarchy, acronym):
    """Find and retunr child with a matching acronym from the next level
    of the hierarchy.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        acronym (str): name of the region

    Returns:
        HierarchyDict: HierarchyDict of the matching child
    """
    for index, child in enumerate(hierarchy["children"]):
        if child["acronym"] == acronym:
            return hierarchy["children"][index]


def positions_to_mask(positions, mask, orientation) -> BoolArray:
    """Change x,y,z position coordinates into binary mask in 3D BoolArray

    Args:
        positions (np.array): 2D : x,y,z positions
        mask (BoolArray): mask sample to reproduce the dimensions
        orientation (VoxelData): orientation field of the atlas

    Returns:
        BoolArray: mask of the region described by the positions
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
    children_names,
) -> None:
    """Edit in place the hierarchy to include new children volumes of a given
    region. Implemented to integrated the barrels into layer 4 of the Barrel
    cortex in Somatosensory cortex.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        new_ids (Dict[int, Dict[str, int]]): set of new ids
        region_map (RegionMap):  map to navigate the brain regions hierarchy.
        start_index (int): index of the starting brain region (Isocortex)
        children_names (list): list of children volumes to be integrated
    """

    hierarchy_levels = np.array(
        region_map.get(start_index, attr="acronym", with_ascendants=True)
    )
    iso_index = np.where(hierarchy_levels == "Isocortex")[0][0]
    hierarchy_levels = hierarchy_levels[:iso_index]
    hierarchy_ = get_isocortex_hierarchy(hierarchy)

    for acronym in hierarchy_levels[::-1]:
        hierarchy_ = get_hierarchy_by_acronym(hierarchy_, acronym)

    new_children = []
    for name in children_names:
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
    """Edit in place layer 4 `volume` to incorporate children volumes of barrels.

    Args:
        volume (NDArray): whole brain annotated volume.
        barrel_positions (pd.DataFrame): x,y,z voxel positions
        atlas (voxelbrain.LocalAtlas): _description_
        region (str): name of the parent region
        region_id (int): parent region id
        new_ids (Dict[str, int]): set of new ids
    """
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


def split_barrels(
    hierarchy: HierarchyDict,
    annotation: VoxelData,
    barrel_positions: pd.DataFrame,
    atlas,
):
    """
    Introduces the barrels specified by a DataFrame to layer 4 of
    barrel cortex region in place.

    The `hierarchy` dict and the `annotation` are modified in-place.
    All of the barrels present in the DF are introduced based on their
    x, y, z voxel positions.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        annotation (VoxelData): whole brain annotation
        barrel_positions (pd.DataFrame): x,y,z voxel positions
        atlas (voxelbrain.LocalAtlas): brain atlas
    """
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
        ssp_bfd4_index,
        barrel_names,
    )

    edit_volume(
        annotation, barrel_positions, atlas, "SSp-bfd4", ssp_bfd4_index, new_ids
    )
