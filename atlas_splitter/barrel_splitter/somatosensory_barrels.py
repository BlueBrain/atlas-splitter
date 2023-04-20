"""
Algorithm introducing volumes of 33 barrel columns coming from segmentation of the 
average brain atlas images from Allen institute. Barrel columns are introduced as children 
to somatosensory area of barrel cortex and then subdivided into layers. 

* Introduction of barrels to the hierarchy.json
* Introduction of the annotated volumes to the annotations.nrrd

The code relays on pd.DataFrame containing the annotated positions of each barrel voxel
in x,y,z coordinates.
"""
import copy
import logging
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from voxcell import RegionMap, VoxelData

from atlas_splitter.utils import create_id_generator, get_isocortex_hierarchy

L = logging.getLogger(__name__)
HierarchyDict = Dict[str, Any]


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


def add_hierarchy_child(parent, id, name, acronym):
    """"""
    """Add barrel-child"""
    new_child = copy.deepcopy(parent)
    new_child["parent_structure_id"] = parent["id"]
    new_child["acronym"] = acronym
    new_child["name"] = name
    new_child["id"] = id
    new_child["st_level"] = parent["st_level"] + 1
    new_child["graph_order"] = parent["graph_order"] + 1

    return new_child


def edit_hierarchy(
    hierarchy: HierarchyDict,
    new_ids: Dict[int, Dict[str, int]],
    region_map: RegionMap,
    start_index: int,
    children_names,
    layers,
) -> None:
    """Edit in place the hierarchy to include new children volumes of a given
    region. Implemented to integrated the barrel columns into [SSp-bfd]
    Barrel cortex in Primary Somatosensory cortex.

    Note:
        The following attributes of the created nodes are copies of the
        parent attributes (see see http://api.brain-map.org/doc/Structure.html for some
        definitions):
        - atlas_id
        - color_hex_triplet
        - hemisphere_id (always set to 3 for the AIBS Mouse P56)
        - graph_order (the structure order in a graph flattened via in order traversal)
        - ontology_id (always set to 1 for the AIBS Mouse P56)
        - st_level
        No proper value of graph_order can be set for a new child. This is why it is left
        unchanged.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        new_ids (Dict[int, Dict[str, int]]): set of new ids
        region_map (RegionMap):  map to navigate the brain regions hierarchy.
        start_index (int): index of the starting brain region (Isocortex)
        children_names (list): list of children volumes to be integrated
        layers (list): list of layers to be integrated
    """

    hierarchy_levels = np.array(region_map.get(start_index, attr="acronym", with_ascendants=True))
    iso_index = np.where(hierarchy_levels == "Isocortex")[0][0]
    hierarchy_levels = hierarchy_levels[:iso_index]
    hierarchy_ = get_isocortex_hierarchy(hierarchy)

    for acronym in hierarchy_levels[::-1]:
        hierarchy_ = get_hierarchy_by_acronym(hierarchy_, acronym)

    new_children = hierarchy_["children"]
    for name in children_names:
        new_child = add_hierarchy_child(
            hierarchy_,
            new_ids[name],
            hierarchy_["name"] + f", {name} barrel",
            hierarchy_["acronym"] + f"-{name}",
        )
        new_subchildren = []
        for layer in layers:
            new_subchild = add_hierarchy_child(
                new_child,
                new_ids[name + "_layers"][layer],
                new_child["name"] + f"layer {layer}",
                new_child["acronym"] + f"-{layer}",
            )
            new_subchild["children"] = []
            if layer == "2/3":
                children23 = []
                for sublayer in ["2", "3"]:
                    layer23_subchild = add_hierarchy_child(
                        new_subchild,
                        new_ids[name + "_layers"][sublayer],
                        new_child["name"] + f"layer {sublayer}",
                        new_child["acronym"] + f"-{sublayer}",
                    )
                    layer23_subchild["children"] = []
                    children23.append(layer23_subchild)
                new_subchild["children"] = children23
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
    """Introduce the barrel columns to the barrel cortex in  the mouse atlas
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
    assert "msg" in hierarchy, "Wrong hierarchy input. The AIBS 1.json file is expected."

    region_map = RegionMap.from_dict(hierarchy["msg"][0])

    indices = region_map.find("SSp-bfd", attr="acronym", with_descendants=False)
    ssp_bfd_index = indices.pop()
    barrel_names = np.sort(barrel_positions.barrel.unique())

    layers = ["1", "2/3", "2", "3", "4", "5", "6a", "6b"]
    id_generator = create_id_generator(region_map)
    new_ids = layer_ids(id_generator, barrel_names, layers)

    layers = ["1", "2/3", "4", "5", "6a", "6b"]
    L.info("Editing hierarchy: barrel columns...")
    edit_hierarchy(hierarchy, new_ids, region_map, ssp_bfd_index, barrel_names, layers)

    layers = ["1", "2", "3", "4", "5", "6a", "6b"]
    L.info("Editing annotation: barrel columns...")
    edit_volume(annotation, region_map, barrel_positions, layers, new_ids)
