"""Utils for region splitter unit tests"""

import numpy as np
from voxcell import VoxelData

# The actual AIBS ids as of 2020.04.21.
LAYER_23_IDS = [
    41,
    113,
    163,
    180,
    201,
    211,
    219,
    241,
    251,
    269,
    288,
    296,
    304,
    328,
    346,
    412,
    427,
    430,
    434,
    492,
    556,
    561,
    582,
    600,
    643,
    657,
    667,
    670,
    694,
    755,
    806,
    821,
    838,
    854,
    888,
    905,
    943,
    962,
    965,
    973,
    1053,
    1066,
    1106,
    1127,
    12994,
    182305697,
    312782554,
    312782582,
    312782608,
    312782636,
    480149210,
    480149238,
    480149266,
    480149294,
    480149322,
]


def get_splitting_input_data():
    padding = 1
    x_width = 1
    width = 55  # width along the y and z axes
    raw = np.zeros((2 * padding + x_width, 2 * padding + width, 2 * padding + width), dtype=int)

    ratio = 2.0 / 5.0
    layer_3_top = padding + int((1.0 - ratio) * width)
    layer_2_ids = [195, 524, 606, 747]
    for i, id_ in enumerate(LAYER_23_IDS):
        raw[padding : (padding + x_width), padding : (padding + width), padding + i] = id_
    for i, id_ in enumerate(layer_2_ids):
        raw[
            padding : (padding + x_width),
            (layer_3_top + 1) : (padding + width),
            padding + i,
        ] = id_

    direction_vectors = np.full(raw.shape + (3,), np.nan)
    direction_vectors[
        padding : (padding + x_width),
        padding : (padding + width),
        padding : (padding + width),
        :,
    ] = [0.0, 1.0, 0.0]

    return {
        "annotation": VoxelData(raw, (1.0, 1.0, 1.0)),
        "direction_vectors": direction_vectors,
        "layer_3_top": layer_3_top,
        "ratio": ratio,
    }
