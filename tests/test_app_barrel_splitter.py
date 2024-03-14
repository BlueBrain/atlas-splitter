from pathlib import Path

from atlas_commons.app_utils import assert_properties
from click.testing import CliRunner
from voxcell import RegionMap, VoxelData  # type: ignore

import atlas_splitter.app.cli as tested
from tests.barrel_splitter.utils import get_barrel_splitter_input_data

TEST_PATH = Path(__file__).parent

output_bfd = {
    201,
    329,
    981,
    1038,
    1047,
    1062,
    1070,
    1998,
    1999,
    1013068637,
    1082141991,
    1337935688,
    1420546517,
    1558550786,
    1667660763,
    1714311201,
    1843338795,
    1945434117,
    2072239244,
    2157537321,
    2525505631,
    2563782304,
    2866280389,
    2930307508,
    3188993656,
    3219108088,
    3291535006,
}


def test_split_barrels():
    runner = CliRunner()
    with runner.isolated_filesystem():
        annotation, positions_barrels = get_barrel_splitter_input_data()
        annotation.save_nrrd("annotation.nrrd")
        positions_barrels.reset_index(drop=True).to_feather("positions_barrels.feather")

        result = runner.invoke(
            tested.cli,
            [
                "split-barrel-columns",
                "--annotation-path",
                "annotation.nrrd",
                "--hierarchy-path",
                str(Path(TEST_PATH, "2.json")),
                "--barrels-path",
                "positions_barrels.feather",
                "--output-hierarchy-path",
                "output_hierarchy.json",
                "--output-annotation-path",
                "output_annotation.nrrd",
            ],
        )

        assert result.exit_code == 0, str(result.output)

        input_annotation = VoxelData.load_nrrd("annotation.nrrd")
        output_annotation = VoxelData.load_nrrd("output_annotation.nrrd")
        assert_properties([input_annotation, output_annotation])

        output_region_map = RegionMap.load_json("output_hierarchy.json")

        barrel_cortex_ids = output_region_map.find("SSp-bfd", attr="acronym", with_descendants=True)

        assert barrel_cortex_ids == output_bfd
