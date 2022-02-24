"""
Algorithm splitting the layer 2/3 of the mouse isocortex into
layer 2 and layer 3.

* Splitting layer 2/3 within the input AIBS 1.json hierarchy file

For every node in the brain regions hierarchy tree whose name ends with
"[Ll]ayer 2/3" (and whose acronym ends consistently with "2/3"), we create two
child nodes, one for layer 2 and one for layer 3. If the name of a newly inserted
child node is the name of a node n in the original 1.json, we reuse the identifier
of n as the identifier of the new node and n is removed from the hierarchy tree.

* Splitting the annotated volumes base on the modified hierarchy

This algorithm relies on the computation of voxel-to-(layer boundary) approximate
distances along the direction vectors field.
For each voxel of the original layer 2/3, we compute its approximate distances to the top and
the bottom of this volume. We use subsequently a thickness ratio from the scientific literature to
decide whether a voxel belongs either to layer 2 or layer 3.
"""
from __future__ import annotations

import copy
import logging
from collections import defaultdict
from itertools import count
from typing import Any, Dict, Iterator, Set

import numpy as np
from atlas_commons.typing import BoolArray, FloatArray, NDArray
from cgal_pybind import slice_volume
from voxcell import RegionMap, VoxelData

from atlas_splitter.exceptions import AtlasSplitterError

L = logging.getLogger(__name__)

# The following constants are documented in Section 5.1.1.4 of the release report of the
# Neocortex Tissue Reconstruction.
DEFAULT_L2_THICKNESS = 95.10
DEFAULT_L3_THICKNESS = 225.3199
DEFAULT_RATIO = DEFAULT_L2_THICKNESS / (DEFAULT_L2_THICKNESS + DEFAULT_L3_THICKNESS)

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


def edit_hierarchy(
    hierarchy: HierarchyDict,
    new_layer_ids: Dict[int, Dict[str, int]],
    ids_to_reuse: Dict[int, Dict[str, int]],
    region_map: RegionMap,
    id_generator: Iterator[int],
) -> None:
    """
    Edit in place layer 2/3 into 2 and 3 within the hierarchy dict.

    The children list of every (leaf) node of the HierarchyDict tree whose acronym and name end with
    2/3 is populated with two children. The acronyms and names of the children are those of
    the parent node but with endings replaced by 2 and 3 respectively. A child is assigned a
    distinct and new identifer if there was no node n with the same name and acronym in the original
    hierarchy. Otherwise, the identifier of n is reused and the node n is removed from the
    hierarchy.

    The function is recursive and modifies in-place `hierarchy`, `new_layer_ids` and `ids_to_reuse`.

    Note: Isocortex identifiers correponding to layer 2/3 are assumed to be leaf
    region identifiers. These observations are based on
    http://api.brain-map.org/api/v2/structure_graph_download/1.json.

    Args:
        hierarchy: brain regions hierarchy dict. Modified in place.
        new_layer_ids: defaultdict(dict) whose keys are the identifiers of regions whose acronym
            ends with 2/3 and whose values are dicts of the form
            {"layer_2": <id2>, "layer_3": <id3>} where <id2> and <id3> are generated identifiers.
            The argument `new_layer_ids` is modified in place.
            Example:
            {
                107: {"layer_2": 190705, "layer_3": 190706},
                219: {"layer_2": 190713, "layer_3": 190714},
                299: {"layer_2": 190707, "layer_3": 190708},
                ...
            }
        ids_to_reuse: ids of regions whose names and acronyms end with "2" or "3" but not with
            "2/3". Dict of the same form as `new_layer_ids`. The identifier key indicates which
            node with name ending with "2/3" should reuse an original identifier for its children.
            If the "layer_2" (resp. "layer_3") key exists, the corresponding value should be
            reused for the child in "layer_2" (resp. "layer_3")
            Note: with unmodified AIBS 1.json the only ids to be reused are {195, 747, 524, 606}.
                They correspond to region name endings with "layer 2" only.
        region_map: map to navigate the brain regions hierarchy.
        id_generator: iterator generating new region identifiers.

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
        FIXME(Luc): The meaning of st_level and atlas_id is still unclear at the moment, see
        https://community.brain-map.org/t/what-is-the-meaning-of-atlas-id-and-st-level-in-1-json
    """
    to_delete = []
    for index, child in enumerate(hierarchy["children"]):
        if child["acronym"].endswith(("2", "3")) and not child["acronym"].endswith("2/3"):
            _assert_is_leaf_node(child)  # Satisfied by AIBS 1.json
            num = child["acronym"][-1]
            assert child["name"].endswith(num)  # idem
            ids = region_map.find(child["acronym"][:-1] + "2/3", attr="acronym")
            assert len(ids) == 1  # idem
            ids_to_reuse[ids.pop()][f"layer_{num}"] = child["id"]
            to_delete.append(index)

    for index in sorted(to_delete, reverse=True):
        del hierarchy["children"][index]

    for child in hierarchy["children"]:
        if child["acronym"].endswith("2/3"):
            _assert_is_leaf_node(child)  # Satisfied by AIBS 1.json
            assert child["name"].endswith("2/3")  # idem

            # Create children
            new_children = []
            for layer in ["layer_2", "layer_3"]:
                if child["id"] in ids_to_reuse and layer in ids_to_reuse[child["id"]]:
                    new_layer_ids[child["id"]][layer] = ids_to_reuse[child["id"]][layer]
                else:
                    new_layer_ids[child["id"]][layer] = next(id_generator)
                new_child = copy.deepcopy(child)
                new_child["acronym"] = child["acronym"][:-3]
                new_child["name"] = child["name"][:-3]
                new_child["id"] = new_layer_ids[child["id"]][layer]
                new_child["acronym"] = new_child["acronym"] + layer[-1]
                new_child["name"] = new_child["name"] + layer[-1]
                new_child["parent_structure_id"] = child["id"]
                new_children.append(new_child)

            # Populate the current 2/3 leaf node's children
            child["children"] = new_children
        else:
            edit_hierarchy(child, new_layer_ids, ids_to_reuse, region_map, id_generator)


def _edit_layer_23_hierarchy(
    hierarchy: HierarchyDict,
    region_map: RegionMap,
) -> Dict[int, Dict[str, int]]:
    """
    Edit layer 2/3 into 2 and 3.

    Edit in place `hierarchy` to perform the splitting of layer 2/3 into layer 2 and
    layer 3.

    Args:
        hierarchy: brain regions hierarchy dict.
        region_map: map to navigate the brain regions hierarchy.

    Returns:
        dict of the same form as the argument `new_layer_ids` of
        :fun:`atlas_splitter.layer_splitter.isocortex_layer_23.edit_hierarchy`

    """

    new_layer_ids: Dict[int, Dict[str, int]] = defaultdict(dict)
    ids_to_reuse: Dict[int, Dict[str, int]] = defaultdict(dict)
    isocortex_hierarchy = get_isocortex_hierarchy(hierarchy)
    edit_hierarchy(
        isocortex_hierarchy,
        new_layer_ids,
        ids_to_reuse,
        region_map,
        create_id_generator(region_map),
    )

    return new_layer_ids


def _edit_layer_23_volume(
    volume: NDArray[np.integer],
    layer_2_mask: BoolArray,
    layer_23_ids: Set[int],
    new_layer_ids: Dict[int, Dict[str, int]],
) -> None:
    """
    Edit layer 2/3 into 2 and 3.

    Edit in place `volume` to perform the splitting of layer 2/3 into layer 2 and
    layer 3.

    Args:
        volume: whole brain annotated volume.
        layer_2_mask: binary mask of the voxels sitting in layer 2.
        layer_23_ids: the set of all layer 2/3 identifiers,
            i.e., the identifiers whose corresponding acronyms and names
            end with '2/3'.
        new_layer_ids:
            dict of the same form as the argument `new_layer_ids` of
            :fun:`atlas_splitter.layer_splitter.isocortex_layer_23,py.edit_hierarchy`
    """

    def change_volume(id_: int, new_id: int, layer_mask: BoolArray) -> None:
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

    layer_3_mask = np.invert(layer_2_mask)
    for id_ in layer_23_ids:
        change_volume(id_, new_layer_ids[id_]["layer_2"], layer_2_mask)
        change_volume(id_, new_layer_ids[id_]["layer_3"], layer_3_mask)


def split(
    hierarchy: HierarchyDict,
    annotation: VoxelData,
    direction_vectors: FloatArray,
    thickness_ratio: float = DEFAULT_RATIO,
) -> None:
    """
    Splits in place layer 2/3 into layer 2 and layer 3 based on a relative thickness ratio.

    The `hierarchy` dict and the `annotation` are modified in-place.
    Edits performed in `hierarchy` are independend of the content of `annotation`,

    The ratio is used to determined which voxels of layer 2/3 should sit in
    layer 2 or layer 3.

    New identifiers are created for the voxels located in the layers 2 and 3.


    Args:
        hierarchy: brain regions hierarchy dict.
        region_map: map to navigate the brain regions hierarchy.
        annotation: whole brain annotation.
        direction_vectors: array of shape (W, L, D, 3) if the shape of
            `annotation.raw` is (W, L, D, 3). This array holds a field of unit
            3D vectors reflecting the directions of the isocortex fibers.
        thickness_ratio: ratio of average layer thicknesses, i.e.,
            layer_2 thickness / (layer_2 thickness + layer_3 thickness)
            Defaults to `DEFAULT_RATIO`.
    """
    assert "msg" in hierarchy, "Wrong hierarchy input. The AIBS 1.json file is expected."
    region_map = RegionMap.from_dict(hierarchy["msg"][0])
    isocortex_ids = region_map.find("Isocortex", attr="acronym", with_descendants=True)
    layers_2_and_3_ids = isocortex_ids & region_map.find(
        "@.*2(/3)?$", attr="acronym", with_descendants=True
    )

    # No direction vectors should be [NaN, NaN, NaN] inside the region to split
    volume = np.isin(annotation.raw, list(layers_2_and_3_ids))
    if np.any(np.isnan(direction_vectors[volume])):
        raise AtlasSplitterError(
            "The 3D region to split, that is layer 2/3, contains [NaN, NaN, NaN] "
            "direction vectors. Consider interpolating these vectors by valid ones. "
            "See, e.g., ``atlas-direction-vectors`` documentation and"
            "``atlas-direction-vectors interpolation --help`` in particular."
        )
    L.info("Splitting the layer 2/3 volume using a thickness ratio of %f ...", thickness_ratio)
    # The voxels labeled with 1 (resp. 2) are the voxels whose cortical depth is at most
    # (resp. greater than) `thickness_ratio` times the full thickness of layer 2/3.
    # Note: direction vectors flow from the deepest layer to the shallowest layer.
    splitting = slice_volume(
        volume=volume,
        # Default offset can be of type float if voxcell<=3.0.1
        offset=np.array(annotation.offset, dtype=np.float32),
        voxel_dimensions=annotation.voxel_dimensions,
        vector_field=np.asarray(direction_vectors, dtype=np.float32),
        thicknesses=[1.0 - thickness_ratio, thickness_ratio],
        resolution=0.5,
    )
    layer_23_ids = isocortex_ids & region_map.find("@.*2/3$", attr="acronym", with_descendants=True)

    L.info("Editing hierarchy ...")
    new_layer_ids = _edit_layer_23_hierarchy(
        hierarchy, region_map
    )  # `hierarchy` is edited in-place
    L.info("Editing annotation ...")
    _edit_layer_23_volume(
        annotation.raw,
        splitting == 2,  # the voxels of layer 2 are the shallowest; they are located in slice 2.
        layer_23_ids,
        new_layer_ids,
    )
