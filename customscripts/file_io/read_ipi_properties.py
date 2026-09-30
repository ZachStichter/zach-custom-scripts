from os import PathLike
import numpy as np
from numpy import float64
from numpy.typing import NDArray
from typing import Any

def read_ipi_properties(input_file: str | PathLike[Any], targets: int | list[int] = -1)->tuple[NDArray[float64],list[dict[str,str]|None]]:
    """
    Given an input file, read the ipi properties and return the content and titles corresponding to those items.

    If a target is specified, return only those columns.

    Returned content is of the form ([column_idx:property_array(np.ndarray)],[{title:desc}|None])
    """
    result = np.empty((0,0))
    headers = []


    # Normalize targets to a list or None
    if isinstance(targets, int):
        if targets == -1:
            target_indices = None
        else:
            target_indices = [targets]
    else:
        target_indices = targets

    with open(input_file, "r") as i:
        # don't assume the whole file will fit in memory. This is why the weird iteration
        # consume file to count number of data-containing lines, one at a time
        nlines = sum(1 for line in i if line.strip() and not line.strip().startswith("#"))

        # short circuit if broken or missing data
        if nlines == 0 or not nlines:
            return result, [None]

        # reset to start to actually read, but just the headers
        i.seek(0)
        while True:
            line = i.readline().strip()
            # i-pi header format: # column   1     --> step : The current simulation time step.
            # assumes all headers are in the same block (good assumption as of 2026)
            if not line.startswith("#"):
                break
            elif "-->" in line:
                line = line.split("-->")[1]
                head, tail = line.split(':')
                headers.append({head:tail})

        # return to start to actually read the file
        i.seek(0)
        clean_lines = (line for line in i if line.strip() and not line.strip().startswith("#"))

        # just grab some data so we can learn parameters; normalize to floats
        first_line = next(clean_lines)
        first_line_fields = [float(x) for x in first_line.split()]
        ncols = len(first_line_fields)
        result = np.zeros((nlines, ncols))
        result[0,:] = first_line_fields
        for idx, line in enumerate(clean_lines):
            result[idx+1,:] = [float(x) for x in line.split()]
        if target_indices is not None:
            result = result[:,target_indices]
            if headers:
                headers = [headers[idx] for idx in target_indices if idx < len(headers)]
    return result, headers