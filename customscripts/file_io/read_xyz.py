from os import PathLike
from os.path import splitext
import numpy as np

__provides__ = {
    "read_xyz": "read_xyz",
    "extract_xyz_to_frames": "split_xyz"
}


def read_xyz(input_file: str | PathLike, targets: int | list[int] = -1)->dict[int, dict]:
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

def extract_xyz_to_frames(input_file: str | PathLike, targets: int | list[int]=-1, offset: int=0, skip_first: int=0, ndigits:int|None=None)->int:
    """
    Given an input file, read the *.xyz and extract each frame to a file. File names are in the format of <input_file>_001.xyz, in the location of <input_file>.

    If a target is specified, print only those atoms.

    Returns the number of extracted frames.
    """
    name_iterator = offset
    file_header, file_tail = splitext(input_file)
    if targets == -1 or targets is None:
        target_set = None
    elif isinstance(targets, int):
        target_set = {targets}
    else:
        target_set = set(targets)
    ntargets = str(len(target_set) if target_set else 0)

    with open(input_file, "r") as i:
            # don't assume the whole file will fit in memory. This is why the weird iteration
            # consume file to count number of data-containing lines, one at a time
            nframes = 0
            while True:
                header_line = i.readline()
                if not header_line:
                    break
                try:
                    natoms = int(header_line.strip())
                    nframes += 1
                    for _ in range(natoms + 1):
                        i.readline()
                except ValueError:
                    continue
            nframes -= skip_first
    
            # short circuit if broken or missing data
            if nframes == 0:
                return 0

            # reset to start to actually read
            i.seek(0)

            if ndigits is None:
                ndigits = len(str(nframes))

            for k in range(nframes+skip_first):
                these_lines = []
                nextline = i.readline()
                these_lines.append(nextline)
                for _ in range(int(nextline)+1):
                    nextline = i.readline()
                    these_lines.append(nextline)
                if k >= skip_first:
                    with open(f"{file_header}_{name_iterator}{file_tail}", "w+") as o:
                        for idx, oline in enumerate(these_lines):
                            adj_idx = idx-2
                            if target_set is None or adj_idx in target_set:
                                o.write(oline)
                            elif adj_idx == -1:
                                o.write(oline)
                            elif adj_idx == -2:
                                o.write(f"{ntargets}\n")
                        name_iterator += 1

            return nframes