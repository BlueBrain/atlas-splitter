"""Refine annotations by splitting layers of a brain region"""
import json
import logging

import click
import voxcell  # type: ignore
from atlas_commons.app_utils import (
    EXISTING_FILE_PATH,
    common_atlas_options,
    log_args,
    set_verbose,
    verbose_option,
)

from atlas_splitter.layer_splitter import isocortex_layer_23

L = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@click.group()
def app():
    """Run the splitter CLI"""


@app.command()
@verbose_option
@common_atlas_options
@click.option(
    "--direction-vectors-path",
    type=EXISTING_FILE_PATH,
    required=True,
    help=(
        "Path to the mouse isocortex direction vectors nrrd file."
        "The direction vectors should not be (NaN, NaN, NaN) on any voxel of the layer 2/3 volume."
    ),
)
@click.option("--output-hierarchy-path", required=True, help="Path of the json file to write")
@click.option("--output-annotation-path", required=True, help="Path of the nrrd file to write")
@log_args(L)
def split_isocortex_layer_23(  # pylint: disable=too-many-arguments
    verbose,
    annotation_path,
    hierarchy_path,
    direction_vectors_path,
    output_hierarchy_path,
    output_annotation_path,
):
    """Split the layer 2/3 of the AIBS mouse isocortex and save modified hierarchy and
    annotation files.

    Two new nodes are created in the brain regions tree hierarchy for each subregion of the AIBS
    mouse isocortex whose name and acronym ends with "2/3". If the name of a newly inserted node
    is also the name of a node n in the unmodified ``1.json`` hierarchy tree, we reuse the
    identifier of n to set the identifer of the inserted node and n is deleted.

    Note: The modification of the hierarchy file is independent of the input annotated volume.
    The direction vectors should not be (NaN, NaN, NaN) on any voxel of the layer 2/3 volume.
    """
    set_verbose(L, verbose)

    L.info("Loading files ...")
    annotation = voxcell.VoxelData.load_nrrd(annotation_path)
    with open(hierarchy_path, "r", encoding="utf-8") as h_file:
        hierarchy = json.load(h_file)
    direction_vectors = voxcell.VoxelData.load_nrrd(direction_vectors_path)

    # Splits and updates in place hierarchy and annotations
    L.info("Splitting layer 2/3 in layer 2 and layer 3 ...")
    isocortex_layer_23.split(hierarchy, annotation, direction_vectors.raw)

    L.info("Saving modified hierarchy and annotation files ...")
    with open(output_hierarchy_path, "w", encoding="utf-8") as out:
        json.dump(hierarchy, out, indent=1, separators=(",", ": "))
    annotation.save_nrrd(output_annotation_path)
