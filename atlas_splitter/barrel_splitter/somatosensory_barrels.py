"""
Algorithm introducing volumes of 33 barrel columns coming from segmentation of the
average brain atlas images from Allen institute. Barrel columns are introduced as children
to somatosensory area of barrel cortex and then subdivided into layers. Each barrel is
subdivided into layers. To account for this being used after `layer-splitter` layer 2/3 is
split into 2 and 3.

* Introduction of barrels to the hierarchy.json
* Introduction of the annotated volumes to the annotations.nrrd

The code relays on pd.DataFrame containing the annotated positions of each barrel voxel
in x,y,z coordinates.
"""

import copy
import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from voxcell import RegionMap, VoxelData

from atlas_splitter.utils import _assert_is_leaf_node, get_isocortex_hierarchy, id_from_acronym

L = logging.getLogger(__name__)
HierarchyDict = Dict[str, Any]


def layer_ids(
    region: str, names: List[str], layers: List[str], region_map
) -> Dict[str, Dict[str, int]]:
    """Create a dictionary of ids for the new regions with layer subregions.

    Args:
        region: Base barrel region acronym. Example: SSp-bfd
        names: A list of names of the new regions.
        layers: A list of names of the new layer regions.

    Returns:
        A dictionary that maps each region to a dictionary of its layer subregions and their ids.
    """
    new_ids: Dict[str, Dict[str, int]] = {}
    for name in names:
        new_ids[name] = {}
        new_ids[name][name] = id_from_acronym(region_map, _acronym(region, name))
        for layer_name in layers:
            new_ids[name][layer_name] = id_from_acronym(
                region_map, _acronym(region, name, layer_name)
            )

    return new_ids


def get_hierarchy_by_acronym(hierarchy: HierarchyDict, region_map: RegionMap, start_acronym):
    """Find and return child with a matching acronym from the next level
    of the hierarchy.

    Args:
        hierarchy (HierarchyDict): brain regions hierarchy dict
        region_map (RegionMap): region map object from voxcell
        start_acronym (str): acronym name of the brain region

    Returns:
        HierarchyDict: HierarchyDict of the matching child
    """
    indices = region_map.find(start_acronym, attr="acronym", with_descendants=False)
    start_index = indices.pop()

    hierarchy_levels = np.array(region_map.get(start_index, attr="acronym", with_ascendants=True))
    iso_index = np.where(hierarchy_levels == "Isocortex")[0][0]
    hierarchy_levels = hierarchy_levels[:iso_index]
    hierarchy_ = get_isocortex_hierarchy(hierarchy)

    for acronym in hierarchy_levels[::-1]:
        for index, child in enumerate(hierarchy_["children"]):
            if child["acronym"] == acronym:
                hierarchy_ = hierarchy_["children"][index]

    return hierarchy_


def positions_to_mask(positions: np.ndarray, annotation: VoxelData) -> np.ndarray:
    """Change x, y, z position coordinates into binary mask in 3D boolean array.

    Args:
        positions: A numpy array of shape (n, 3) representing the x, y, z positions.
        annotation: A VoxelData object representing the orientation field of the atlas.

    Returns:
        A numpy array of shape annotation.shape with True values at the indices
        corresponding to the input positions.
    """
    mask = np.zeros(annotation.shape, dtype=bool)
    indices = annotation.positions_to_indices(positions)
    mask[tuple(indices.T)] = True
    return mask


def region_logical_and(positions: np.ndarray, annotation: VoxelData, indices: List) -> np.ndarray:
    """Perform a logical AND operation between the binary mask of a region
    defined by a given set of positions and the binary mask of the region
    specified by the region name. Function used to merge barrel  columns and layers.

    Args:
        positions (np.array): A 2D numpy array of shape (N, 3) containing
            x, y, z coordinates of positions.
        annotation (VoxelData): A VoxelData object representing the orientation
            field of the atlas.
        indices (List): list of indices to be used for region annotation

    Returns:
        np.ndarray: A 3D numpy array of the same shape as `annotation.data` containing
        the resulting binary mask after performing the logical AND operation (bool values).
    """
    mask = positions_to_mask(positions, annotation)
    if len(indices) == 1:
        region_mask = annotation.raw == indices[0]
    else:
        region_mask = np.isin(annotation.raw, indices)
    layer_barrel = np.logical_and(region_mask, mask).astype(bool)
    return layer_barrel


def add_hierarchy_child(
    parent: Dict[str, Any], id_: int, name: str, acronym: str
) -> Dict[str, Any]:
    """
    Add a new child to a hierarchical structure.

    Args:
        parent: The parent structure to which the child is being added.
        id_: The unique identifier for the child.
        name: The name of the child.
        acronym: The acronym for the child.

    Returns:
        A new copy of the parent structure with the child added to it.
    """
    new_child = copy.deepcopy(parent)
    new_child["parent_structure_id"] = parent["id"]
    new_child["acronym"] = acronym
    new_child["name"] = name
    new_child["id"] = id_
    new_child["st_level"] = parent["st_level"] + 1
    new_child["graph_order"] = parent["graph_order"] + 1
    return new_child


def edit_hierarchy(  # pylint: disable=too-many-arguments
    region: str,
    hierarchy: HierarchyDict,
    new_ids: Dict[str, Dict[str, int]],
    region_map: RegionMap,
    layers: List[str],
) -> None:
    """Edit in place the hierarchy to include new children volumes of a given
    region. Implemented to integrate the barrel columns into [SSp-bfd]
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
        region (str): Barrel region acronym. Example: SSp-bdf2
        hierarchy (HierarchyDict): brain regions hierarchy dict
        new_ids (Dict[int, Dict[str, int]]): set of new ids
        region_map (RegionMap): region map object from voxcell
        layers (list): list of layers to be integrated
    """
    # pylint: disable=too-many-locals
    children_names = new_ids.keys()
    hierarchy_ = get_hierarchy_by_acronym(hierarchy, region_map, start_acronym=region)

    new_children = hierarchy_["children"]
    for name in children_names:
        new_barrel = add_hierarchy_child(
            hierarchy_,
            new_ids[name][name],
            f"{hierarchy_['name']}, {name} barrel",
            _acronym(region, name),
        )
        assert new_barrel["acronym"].endswith(name)

        new_barrelchildren = []
        for layer in layers:
            new_barrel_layer = add_hierarchy_child(
                new_barrel,
                new_ids[name][layer],
                f"{new_barrel['name']} layer {layer}",
                _acronym(region, name, layer),
            )
            assert new_barrel_layer["acronym"].endswith(layer)

            new_barrel_layer["children"] = []
            if layer == "2/3":
                children23 = []
                for sublayer in ["2", "3"]:
                    layer23_child = add_hierarchy_child(
                        new_barrel_layer,
                        new_ids[name][sublayer],
                        f"{new_barrel['name']} layer {sublayer}",
                        _acronym(region, name, sublayer),
                    )
                    layer23_child["children"] = []
                    _assert_is_leaf_node(layer23_child)

                    children23.append(layer23_child)

                new_barrel_layer["children"] = children23
            else:
                _assert_is_leaf_node(new_barrel_layer)

            new_barrelchildren.append(new_barrel_layer)

        new_barrel["children"] = new_barrelchildren
        new_children.append(new_barrel)

    hierarchy_["children"] = new_children


def _acronym(region_acronym, layer=None, sublayer=None):
    final_acronym = region_acronym
    if layer:
        final_acronym += f"-{layer}"

    if sublayer:
        assert layer is not None, "Sublayer name needs a layer name too, but None passed."
        final_acronym += f"-{sublayer}"

    return final_acronym


def edit_volume(
    annotation: VoxelData,
    region_map: RegionMap,
    barrel_positions: pd.DataFrame,
    layers: List[str],
    new_ids: Dict[str, Dict[str, int]],
) -> None:
    """Edit in place the volume of the barrel cortex to include the barrel columns as
    separate ids. Implemented to integrate the barrel columns into [SSp-bfd] Barrel
    cortex in Primary Somatosensory cortex. The columns are also subdivided into layers.

    Args:
        annotation (VoxelData): whole brain annotation
        region_map (RegionMap): region map object from voxcell
        barrel_positions (pd.DataFrame): x,y,z voxel positions
        layers (list): list of layers to be integrated
        new_ids (Dict[int, Dict[str, int]]): set of new ids
    """
    for name in barrel_positions.barrel.unique():
        positions = barrel_positions[barrel_positions.barrel == name][["x", "y", "z"]].values
        for layer in layers:
            region = f"SSp-bfd{layer}"
            new_id = new_ids[name][layer]
            region_indices = list(region_map.find(region, attr="acronym", with_descendants=True))
            layer_barrel = region_logical_and(positions, annotation, region_indices)

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
    region = "SSp-bfd"
    assert "msg" in hierarchy, "Wrong hierarchy input. The AIBS 1.json file is expected."

    region_map = RegionMap.from_dict(hierarchy["msg"][0])
    barrel_names = sorted(barrel_positions.barrel.unique())

    layers = ["1", "2/3", "2", "3", "4", "5", "6a", "6b"]
    new_ids = layer_ids(region, barrel_names, layers, region_map)

    layers = ["1", "2/3", "4", "5", "6a", "6b"]
    L.info("Editing hierarchy: barrel columns...")
    edit_hierarchy(region, hierarchy, new_ids, region_map, layers)

    layers = ["1", "2", "3", "4", "5", "6a", "6b"]
    L.info("Editing annotation: barrel columns...")
    edit_volume(annotation, region_map, barrel_positions, layers, new_ids)
