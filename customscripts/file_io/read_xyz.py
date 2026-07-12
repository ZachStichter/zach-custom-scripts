from os import PathLike
import numpy as np


def read_xyz(input_file: str | PathLike, targets: int | list[int] = -1):
    """
    Given an input file, read the *.xyz and return the content.

    If a target is specified, return only those atoms.

    Returned content is of the form {atom_index:{symbol:str, x:np.ndarray, y:np.ndarray, z:np.ndarray}}
    """
    result = {}

    with open(input_file, "r") as i:
        lines = i.readlines()

    if not lines:
        return result

    # Normalize targets to a list
    if isinstance(targets, int):
        if targets == -1:
            target_indices = None
        else:
            target_indices = [targets]
    else:
        target_indices = targets

    # Parse trajectory style .xyz file
    line_idx = 0
    frame_idx = 0

    while line_idx < len(lines):
        try:
            num_atoms = int(lines[line_idx].strip())
        except (ValueError, IndexError):
            break

        # Skip comment line
        line_idx += 2

        if line_idx + num_atoms > len(lines):
            break

        atom_lines = lines[line_idx : line_idx + num_atoms]

        frame_data = {}
        for atom_idx, line in enumerate(atom_lines):
            if target_indices is None or atom_idx in target_indices:
                parts = line.split()
                symbol = parts[0]
                x = np.float64(parts[1])
                y = np.float64(parts[2])
                z = np.float64(parts[3])
                frame_data[atom_idx] = {"symbol": symbol, "x": x, "y": y, "z": z}

        for atom_idx, data in frame_data.items():
            if atom_idx not in result:
                result[atom_idx] = {"symbol": data["symbol"], "x": [], "y": [], "z": []}
            result[atom_idx]["x"].append(data["x"])
            result[atom_idx]["y"].append(data["y"])
            result[atom_idx]["z"].append(data["z"])
        frame_idx += 1
        line_idx += num_atoms

    for atom_idx, data in result.items():
        result[atom_idx]["x"] = np.array(result[atom_idx]["x"])
        result[atom_idx]["y"] = np.array(result[atom_idx]["y"])
        result[atom_idx]["z"] = np.array(result[atom_idx]["z"])
    return result
