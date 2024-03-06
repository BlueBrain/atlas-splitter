import pytest
from voxcell import RegionMap
from pathlib import Path

PWD = Path(__file__).parent


@pytest.fixture(scope="session")
def region_map():
    return RegionMap.load_json(PWD / "1.json")

