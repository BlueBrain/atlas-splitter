import numpy as np
import pandas as pd
from voxcell import VoxelData


def get_barrel_cortex_excerpt():
    return {
        "id": 0,
        "msg": [
            {
                "id": 315,
                "acronym": "Isocortex",
                "name": "Isocortex",
                "children": [
                    {
                        "id": 329,
                        "acronym": "SSp-bfd",
                        "name": "Primary somatosensory area, barrel field",
                        "st_level": 9,
                        "parent_structure_id": 322,
                        "graph_order": 51,
                        "children": [
                            {
                                "id": 981,
                                "acronym": "SSp-bfd1",
                                "name": "Primary somatosensory area, barrel field, layer 1",
                                "graph_order": 52,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 201,
                                "acronym": "SSp-bfd2/3",
                                "name": "Primary somatosensory area, barrel field, layer 2/3",
                                "graph_order": 53,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [
                                    {
                                        "id": 1998,
                                        "ontology_id": 1,
                                        "acronym": "SSp-bfd2",
                                        "name": "Primary somatosensory area, barrel field, layer 2",
                                        "graph_order": 53,
                                        "st_level": 11,
                                        "hemisphere_id": 3,
                                        "parent_structure_id": 201,
                                        "children": [],
                                        "layers": ["2"],
                                    },
                                    {
                                        "id": 1999,
                                        "ontology_id": 1,
                                        "acronym": "SSp-bfd3",
                                        "name": "Primary somatosensory area, barrel field, layer 3",
                                        "graph_order": 53,
                                        "st_level": 11,
                                        "hemisphere_id": 3,
                                        "parent_structure_id": 201,
                                        "children": [],
                                        "layers": ["3"],
                                    },
                                ],
                            },
                            {
                                "id": 1047,
                                "acronym": "SSp-bfd4",
                                "name": "Primary somatosensory area, barrel field, layer 4",
                                "graph_order": 54,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1070,
                                "acronym": "SSp-bfd5",
                                "name": "Primary somatosensory area, barrel field, layer|5",
                                "graph_order": 55,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1038,
                                "acronym": "SSp-bfd6a",
                                "name": "Primary somatosensory area, barrel field, layer 6a",
                                "graph_order": 56,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1062,
                                "acronym": "SSp-bfd6b",
                                "name": "Primary somatosensory area, barrel field, layer 6b",
                                "graph_order": 57,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                        ],
                    }
                ],
            }
        ],
    }


def get_barrel_cortex_excerpt_edited():
    return {
        "id": 0,
        "msg": [
            {
                "id": 315,
                "acronym": "Isocortex",
                "name": "Isocortex",
                "children": [
                    {
                        "id": 329,
                        "acronym": "SSp-bfd",
                        "name": "Primary somatosensory area, barrel field",
                        "st_level": 9,
                        "parent_structure_id": 322,
                        "graph_order": 51,
                        "children": [
                            {
                                "id": 981,
                                "acronym": "SSp-bfd1",
                                "name": "Primary somatosensory area, barrel field, layer 1",
                                "graph_order": 52,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 201,
                                "acronym": "SSp-bfd2/3",
                                "name": "Primary somatosensory area, barrel field, layer 2/3",
                                "graph_order": 53,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [
                                    {
                                        "id": 1998,
                                        "ontology_id": 1,
                                        "acronym": "SSp-bfd2",
                                        "name": "Primary somatosensory area, barrel field, layer 2",
                                        "graph_order": 53,
                                        "st_level": 11,
                                        "hemisphere_id": 3,
                                        "parent_structure_id": 201,
                                        "children": [],
                                        "layers": ["2"],
                                    },
                                    {
                                        "id": 1999,
                                        "ontology_id": 1,
                                        "acronym": "SSp-bfd3",
                                        "name": "Primary somatosensory area, barrel field, layer 3",
                                        "graph_order": 53,
                                        "st_level": 11,
                                        "hemisphere_id": 3,
                                        "parent_structure_id": 201,
                                        "children": [],
                                        "layers": ["3"],
                                    },
                                ],
                            },
                            {
                                "id": 1047,
                                "acronym": "SSp-bfd4",
                                "name": "Primary somatosensory area, barrel field, layer 4",
                                "graph_order": 54,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1070,
                                "acronym": "SSp-bfd5",
                                "name": "Primary somatosensory area, barrel field, layer|5",
                                "graph_order": 55,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1038,
                                "acronym": "SSp-bfd6a",
                                "name": "Primary somatosensory area, barrel field, layer 6a",
                                "graph_order": 56,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 1062,
                                "acronym": "SSp-bfd6b",
                                "name": "Primary somatosensory area, barrel field, layer 6b",
                                "graph_order": 57,
                                "st_level": 11,
                                "parent_structure_id": 329,
                                "children": [],
                            },
                            {
                                "id": 2010,
                                "acronym": "SSp-bfd-C1",
                                "name": "Primary somatosensory area, barrel field, C1 barrel",
                                "st_level": 10,
                                "parent_structure_id": 329,
                                "graph_order": 52,
                                "children": [
                                    {
                                        "id": 2011,
                                        "acronym": "SSp-bfd-C1-1",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 1",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2014,
                                        "acronym": "SSp-bfd-C1-2/3",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 2/3",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [
                                            {
                                                "id": 2012,
                                                "acronym": "SSp-bfd-C1-2",
                                                "name": "Primary somatosensory area, barrel field, C1 barrel layer 2",
                                                "st_level": 12,
                                                "parent_structure_id": 2014,
                                                "graph_order": 54,
                                                "children": [],
                                            },
                                            {
                                                "id": 2013,
                                                "acronym": "SSp-bfd-C1-3",
                                                "name": "Primary somatosensory area, barrel field, C1 barrel layer 3",
                                                "st_level": 12,
                                                "parent_structure_id": 2014,
                                                "graph_order": 54,
                                                "children": [],
                                            },
                                        ],
                                    },
                                    {
                                        "id": 2015,
                                        "acronym": "SSp-bfd-C1-4",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 4",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2016,
                                        "acronym": "SSp-bfd-C1-5",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 5",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2017,
                                        "acronym": "SSp-bfd-C1-6a",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 6a",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2018,
                                        "acronym": "SSp-bfd-C1-6b",
                                        "name": "Primary somatosensory area, barrel field, C1 barrel layer 6b",
                                        "st_level": 11,
                                        "parent_structure_id": 2010,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                ],
                            },
                            {
                                "id": 2000,
                                "acronym": "SSp-bfd-C2",
                                "name": "Primary somatosensory area, barrel field, C2 barrel",
                                "st_level": 10,
                                "parent_structure_id": 329,
                                "graph_order": 52,
                                "children": [
                                    {
                                        "id": 2001,
                                        "acronym": "SSp-bfd-C2-1",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 1",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2004,
                                        "acronym": "SSp-bfd-C2-2/3",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 2/3",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [
                                            {
                                                "id": 2002,
                                                "acronym": "SSp-bfd-C2-2",
                                                "name": "Primary somatosensory area, barrel field, C2 barrel layer 2",
                                                "st_level": 12,
                                                "parent_structure_id": 2004,
                                                "graph_order": 54,
                                                "children": [],
                                            },
                                            {
                                                "id": 2003,
                                                "acronym": "SSp-bfd-C2-3",
                                                "name": "Primary somatosensory area, barrel field, C2 barrel layer 3",
                                                "st_level": 12,
                                                "parent_structure_id": 2004,
                                                "graph_order": 54,
                                                "children": [],
                                            },
                                        ],
                                    },
                                    {
                                        "id": 2005,
                                        "acronym": "SSp-bfd-C2-4",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 4",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2006,
                                        "acronym": "SSp-bfd-C2-5",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 5",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2007,
                                        "acronym": "SSp-bfd-C2-6a",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 6a",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                    {
                                        "id": 2008,
                                        "acronym": "SSp-bfd-C2-6b",
                                        "name": "Primary somatosensory area, barrel field, C2 barrel layer 6b",
                                        "st_level": 11,
                                        "parent_structure_id": 2000,
                                        "graph_order": 53,
                                        "children": [],
                                    },
                                ],
                            },
                        ],
                    }
                ],
            }
        ],
    }


def get_barrel_splitter_input_data():
    padding = 1
    x_width = 1
    width = 55  # width along the y and z axes
    raw = np.zeros((2 * padding + x_width, 2 * padding + width, 2 * padding + width), dtype=int)

    raw[1, 0:5, :] = 981
    raw[1, 5:10, :] = 1998
    raw[1, 10:20, :] = 1999
    raw[1, 20:30, :] = 1047
    raw[1, 30:40, :] = 1070
    raw[1, 40:50, :] = 1038
    raw[1, 50:, :] = 1062

    positions_barrel_C2 = pd.DataFrame(
        {
            "x": np.ones(57),
            "y": np.arange(0, 57),
            "z": np.ones(57) * 10,
            "barrel": np.repeat("C2", 57),
        }
    )
    positions_barrel_C1 = pd.DataFrame(
        {
            "x": np.ones(57),
            "y": np.arange(0, 57),
            "z": np.ones(57) * 20,
            "barrel": np.repeat("C1", 57),
        }
    )

    positions_barrels = pd.concat([positions_barrel_C2, positions_barrel_C1])

    return VoxelData(raw.copy(), (1.0, 1.0, 1.0)), positions_barrels
