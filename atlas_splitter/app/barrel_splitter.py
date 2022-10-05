import os
import json
import voxcell
import pandas as pd

from atlas_splitter.barrel_splitter import somatosensory_barrels
from voxcell.nexus.voxelbrain import Atlas

atlas_path = "/gpfs/bbp.cscs.ch/data/project/proj100/atlas_work/mouse/atlases/20210531/"

barrel_positions = pd.read_feather(
    "/gpfs/bbp.cscs.ch/project/proj100/atlas_work/mouse/atlas_mouse/data/fixed_annotated_barrels.f"
)

atlas = Atlas.open(atlas_path)

annotation_path = os.path.join(atlas_path, "brain_regions.nrrd")
annotation = voxcell.VoxelData.load_nrrd(annotation_path)

hierarchy_path = os.path.join(atlas_path, "hierarchy.json")

with open(hierarchy_path, "r", encoding="utf-8") as h_file:
    hierarchy = json.load(h_file)

somatosensory_barrels.split_barrels(hierarchy, annotation.raw, barrel_positions, atlas)


output_hierarchy_path = "/gpfs/bbp.cscs.ch/project/proj100/atlas_work/mouse/atlases/modification/hierarchy.json"
output_annotation_path = "/gpfs/bbp.cscs.ch/project/proj100/atlas_work/mouse/atlases/modification/brain_regions.nrrd"

with open(output_hierarchy_path, "w", encoding="utf-8") as out:
    json.dump(hierarchy, out, indent=1, separators=(",", ": "))

annotation.save_nrrd(output_annotation_path)
