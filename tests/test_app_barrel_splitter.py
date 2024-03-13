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
    1050271831,
    1419828837,
    1541598958,
    1561898146,
    1669999094,
    1742227897,
    1779524838,
    1914058509,
    1941812702,
    2061835172,
    2112620658,
    2190770412,
    2321675771,
    2491030215,
    3335143301,
    3364575989,
    3625413550,
    3951617891,
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
