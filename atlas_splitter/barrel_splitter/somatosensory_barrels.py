"""
Algorithm introducing volumes of 33 barrel columns coming from segmentation of the 
average brain atlas images from Allen institute. Barrel columns are introduced as children 
to somatosensory area of barrel cortex and then subdivided into layers. 

* Introduction of barrels to the hierarchy.json
* Introduction of the annotated volumes to the annotations.nrrd

The code relays on pd.DataFrame contaaining the annotated positions of each barrel voxel
in x,y,z coordinates.
"""
import copy
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Iterator, List
from itertools import count
from collections import defaultdict
from voxcell import RegionMap, VoxelData
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
    the previous ones and from the ident ifiers in use in `self.region_map`.

    Args:
        region_map: map to navigate the brain region hierarchy.

    Returns:
        iterator providing the next id.
    """
    last = max(region_map.find("root", attr="acronym", with_descendants=True))
    return count(start=last + 1)


def layer_ids(id_generator, names, layers):
    """Create a dictionary of ids for the new regions with layer subregions.

    Args:
        id_generator (Iterator[int]): generator of new ids
        names (List[str]): names of the new regions
        layers (List[str]): names of the new layer regions

    Returns:
        Dict[int, Dict[str, int]]: dictionary of ids for the new regions
    """
    new_ids: Dict[int, Dict[str, int]] = defaultdict(dict)

    for name in names:
        new_ids[name] = next(id_generator)
        new_ids[name + "_layers"] = {}
        for layer_name in layers:
            new_ids[name + "_layers"][layer_name] = next(id_generator)

    return new_ids


def get_hierarchy_by_acronym(hierarchy, acronym):
    """Find and return child with a matching acronym from the next level
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


def positions_to_mask(positions, annotation):
    """Change x,y,z position coordinates into binary mask in 3D BoolArray

    Args:
        positions (np.array): 2D : x,y,z positions
        annotation (VoxelData): orientation field of the atlas

    Returns:
        BoolArray: mask of the region described by the positions
    """

    mask = np.zeros(annotation.shape)
    indices = annotation.positions_to_indices(positions)

    for indx in indices:
        mask[indx[0], indx[1], indx[2]] = True

    return mask


def region_logical_and(positions, region, annotation, region_map):
    """Logical and of the region mask and the positions mask (used to merge columns and layers)

    Args:
        positions (np.array): 2D : x,y,z positions
        region (str): name of the region
        annotation (VoxelData): orientation field of the atlas
        region_map (RegionMap): map to navigate the brain regions hierarchy.

    Returns:
        BoolArray: mask of the region described by the positions
    """
    mask = positions_to_mask(positions, annotation).astype(bool)
    indices = np.isin(
        annotation.raw,
        list(region_map.find(region, attr="acronym", with_descendants=True)),
    ).astype(bool)
    layer_barrel = np.logical_and(indices, mask).astype(bool)

    return layer_barrel


def edit_hierarchy(
    hierarchy: HierarchyDict,
    new_ids: Dict[int, Dict[str, int]],
    region_map: RegionMap,
    start_index: int,
    children_names,
) -> None:
    """Edit in place the hierarchy to include new children volumes of a given
    region. Implemented to integrated the barrel columns into [SSp-bfd]
    Barrel cortex in Primary Somatosensory cortex.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        new_ids (Dict[int, Dict[str, int]]): set of new ids
        region_map (RegionMap):  map to navigate the brain regions hierarchy.
        start_index (int): index of the starting brain region (Isocortex)
        children_names (list): list of children volumes to be integrated
    """

    hierarchy_levels = np.array(region_map.get(start_index, attr="acronym", with_ascendants=True))
    iso_index = np.where(hierarchy_levels == "Isocortex")[0][0]
    hierarchy_levels = hierarchy_levels[:iso_index]
    hierarchy_ = get_isocortex_hierarchy(hierarchy)

    for acronym in hierarchy_levels[::-1]:
        hierarchy_ = get_hierarchy_by_acronym(hierarchy_, acronym)

    new_children = hierarchy_["children"]
    for name in children_names:
        new_child = copy.deepcopy(hierarchy_)
        new_child["parent_structure_id"] = hierarchy_["id"]
        new_child["acronym"] = hierarchy_["acronym"] + f"-{name}"
        new_child["name"] = hierarchy_["name"] + f", {name} barrel"
        new_child["id"] = new_ids[name]
        new_child["st_level"] = hierarchy_["st_level"] + 1
        new_child["graph_order"] = hierarchy_["graph_order"] + 1
        new_subchildren = []

        layers = list(new_ids[f"{name}_layers"].keys())
        for layer in layers:
            new_subchild = copy.deepcopy(new_child)
            new_subchild["parent_structure_id"] = new_child["id"]
            new_subchild["acronym"] = new_child["acronym"] + f"-{layer}"
            new_subchild["name"] = new_child["name"] + f"layer {layer}"
            new_subchild["id"] = new_ids[name + "_layers"][layer]
            new_subchild["st_level"] = new_child["st_level"] + 1
            new_subchild["graph_order"] = new_child["graph_order"] + 1
            new_subchild["children"] = []
            new_subchildren.append(new_subchild)

        new_child["children"] = new_subchildren
        new_children.append(new_child)

    hierarchy_["children"] = new_children


def edit_volume(
    annotation: VoxelData,
    region_map: RegionMap,
    barrel_positions: pd.DataFrame,
    layers: List[str],
    new_ids: Dict[str, int],
):
    """Edit in place the volume of the barrel cortex to include the barrel columns as
    separate ids. Implemented to integrated the barrel columns into [SSp-bfd] Barrel
    cortex in Primary Somatosensory cortex. The columns are also subdivided into layers.

    Args:
        volume (NDArray): whole brain annotated volume.
        barrel_positions (pd.DataFrame): x,y,z voxel positions
        new_ids (Dict[str, int]): set of new ids
    """
    for name in barrel_positions.barrel.unique():
        positions = barrel_positions[barrel_positions.barrel == name][["x", "y", "z"]].values
        for layer in layers:
            region = f"SSp-bfd{layer}"
            new_id = new_ids[name + "_layers"][layer]
            layer_barrel = region_logical_and(positions, region, annotation, region_map)

            annotation.raw[layer_barrel] = new_id


def split_barrels(
    hierarchy: HierarchyDict,
    annotation: VoxelData,
    barrel_positions: pd.DataFrame,
):
    """Introduce the barrel columns to the barrel cortex in the mouse atlas
    annotation in place. Positions of the voxels need to be specified by a DataFrame.
    Each column is subdivided into layers.

    The `hierarchy` dict and the `annotation` are modified in-place.
    All of the barrels present in the DF are introduced based on their
    x, y, z voxel positions.


    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        annotation (VoxelData): whole brain annotation
        barrel_positions (pd.DataFrame): x,y,z voxel positions
    """
    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    indices = region_map.find("SSp-bfd", attr="acronym", with_descendants=False)
    ssp_bfd_index = indices.pop()
    barrel_names = np.sort(barrel_positions.barrel.unique())

    layers = ["1", "2", "3", "2/3", "4", "5", "6a", "6b"]
    id_generator = create_id_generator(region_map)
    new_ids = layer_ids(id_generator, barrel_names, layers)

    edit_hierarchy(hierarchy, new_ids, region_map, ssp_bfd_index, barrel_names)
    edit_volume(annotation, region_map, barrel_positions, layers, new_ids)
