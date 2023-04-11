import json
import logging
import click
import pandas as pd

from atlas_splitter.barrel_splitter import somatosensory_barrels
from voxcell import VoxelData
from atlas_commons.app_utils import (
    EXISTING_FILE_PATH,
    common_atlas_options,
    log_args,
    set_verbose,
    verbose_option,
)

L = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@click.group()
def app():
    """Run the splitter CLI"""


@app.command()
@verbose_option
@common_atlas_options
@click.option(
    "--barrels-path",
    type=EXISTING_FILE_PATH,
    required=True,
    help=("Path to the DataFrame with barrel positions and labels."),
)
@click.option(
    "--output-hierarchy-path", required=True, help="Path of the json file to write"
)
@click.option(
    "--output-annotation-path", required=True, help="Path of the nrrd file to write"
)
@log_args(L)
def split_barrel_columns(
    verbose,
    annotation_path,
    hierarchy_path,
    barrels_path,
    output_hierarchy_path,
    output_annotation_path,
):
    """Introduce the barrel columns to SSp-bfd (primary somatosensory barrel cortex)
    in the mouse annotations in place. Positions of the voxels need to be specified by a DataFrame.

    The `hierarchy` dict and the `annotation` are modified in-place.
    All of the barrels present in the DF are introduced based on their
    x, y, z voxel positions.

    New children are added to the layer 4 of Somatosensory barrel cortex
    in Isocortex.
    """
    set_verbose(L, verbose)

    L.info("Loading files ...")
    barrel_positions = pd.read_feather(barrels_path)
    annotation = VoxelData.load_nrrd(annotation_path)

    with open(hierarchy_path, "r", encoding="utf-8") as h_file:
        hierarchy = json.load(h_file)

    L.info("Introduce the barrel columns to SSp-bfd...")
    somatosensory_barrels.split_barrels(hierarchy, annotation, barrel_positions)

    L.info("Saving modified hierarchy and annotation files ...")
    with open(output_hierarchy_path, "w", encoding="utf-8") as out:
        json.dump(hierarchy, out, indent=1, separators=(",", ": "))
    annotation.save_nrrd(output_annotation_path)
