"""test app.layer_splitter"""
from pathlib import Path

from atlas_commons.app_utils import assert_properties
from click.testing import CliRunner
from voxcell import RegionMap, VoxelData  # type: ignore

import atlas_splitter.app.layer_splitter as tested
from tests.layer_splitter.utils import LAYER_23_IDS, get_splitting_input_data

TEST_PATH = Path(__file__).parent


def _get_result(runner):
    return runner.invoke(
        tested.app,
        [
            "split-isocortex-layer-23",
            "--annotation-path",
            "annotation.nrrd",
            "--hierarchy-path",
            str(Path(TEST_PATH, "1.json")),
            "--direction-vectors-path",
            "direction_vectors.nrrd",
            "--output-hierarchy-path",
            "output_hierarchy.json",
            "--output-annotation-path",
            "output_annotation.nrrd",
        ],
    )


def _create_files():
    data = get_splitting_input_data()
    annotation = data["annotation"]
    annotation.save_nrrd("annotation.nrrd")
    direction_vectors = data["direction_vectors"]
    annotation.with_data(direction_vectors).save_nrrd("direction_vectors.nrrd")


def test_split_isocortex_layer_23():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create_files()
        result = _get_result(runner)
        assert result.exit_code == 0, str(result.output)

        input_annotation = VoxelData.load_nrrd("annotation.nrrd")
        output_annotation = VoxelData.load_nrrd("output_annotation.nrrd")
        assert_properties([input_annotation, output_annotation])

        output_region_map = RegionMap.load_json("output_hierarchy.json")
        isocortex_23_ids = output_region_map.find(
            "Isocortex", attr="acronym", with_descendants=True
        )
        isocortex_23_ids = isocortex_23_ids & output_region_map.find(
            "@.*[Ll]ayer 2/3$", attr="name", with_descendants=False
        )
        assert isocortex_23_ids == set(LAYER_23_IDS)
