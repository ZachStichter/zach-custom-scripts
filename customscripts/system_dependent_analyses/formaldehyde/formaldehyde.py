from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import customscripts

__provides__ = {
    "process_traj": "process_formaldehyde_traj_to_dch_doh",
    "calculate_reactive_flux_parameters": "reactive_flux_params_formaldehyde_dch_doh",
    "satisfies_rc_condition": "check_formaldehyde_d_dch_doh_geq_zero"
}


def process_traj(
    trajfile: Union[str, Path],
    cutoff: float = 0.2,
) -> Tuple[
    Optional[Dict[str, Any]],
    Optional[Dict[str, Any]],
    Optional[Dict[str, Any]],
    Optional[Any],
    Optional[Any],
    Optional[np.ndarray],
]:
    """Processes a trajectory file and calculates C-H1 vs O-H1 distance differences.

    Reads an XYZ trajectory file, discards the initial fraction of frames based on
    the cutoff parameter, extracts atom positions, and computes geometric distance
    metrics across the remaining trajectory frames.

    Args:
        trajfile (str | Path): Path to the trajectory file to be processed.
        cutoff (float, optional): Fraction of initial frames to ignore (0.0 <= cutoff < 1.0).
            Defaults to 0.2.

    Returns:
        tuple: A 6-element tuple containing:
            - c_pos (dict | None): Sliced x, y, z positions for Carbon (atom index 0).
            - o_pos (dict | None): Sliced x, y, z positions for Oxygen (atom index 1).
            - h1_pos (dict | None): Sliced x, y, z positions for Hydrogen 1 (atom index 2).
            - l_x (Any | None): Box length/data along x (from atom/key index 4).
            - l_y (Any | None): Box length/data along y (from atom/key index 5).
            - d_diff (np.ndarray | None): Frame-wise difference between C-H1 and O-H1 distances.

            Returns (None, None, None, None, None, None) if the trajectory is empty,
            invalid, or contains fewer than 6 entries.

    Raises:
        ValueError: If `cutoff` is outside the range [0.0, 1.0).
    """
    if not (0.0 <= cutoff < 1.0):
        raise ValueError("cutoff must be a float between 0.0 and 1.0 (exclusive).")

    traj = customscripts.read_xyz(trajfile)

    # Early exit if trajectory is empty or missing required indices (0 through 5)
    if not traj or len(traj) < 6:
        return (None, None, None, None, None, None)

    frames = len(traj[0]["x"])
    cutoff_idx = int(cutoff * frames)

    # Extract positions post-cutoff
    c_pos = {axis: traj[0][axis][cutoff_idx:] for axis in ("x", "y", "z")}
    o_pos = {axis: traj[1][axis][cutoff_idx:] for axis in ("x", "y", "z")}
    h1_pos = {axis: traj[2][axis][cutoff_idx:] for axis in ("x", "y", "z")}

    l_x = traj[4]["x"][cutoff_idx:]
    l_y = traj[5]["y"][cutoff_idx:]

    # Calculate interatomic distances and distance difference
    dch = np.sqrt(
        (c_pos["x"] - h1_pos["x"]) ** 2
        + (c_pos["y"] - h1_pos["y"]) ** 2
        + (c_pos["z"] - h1_pos["z"]) ** 2
    )
    doh = np.sqrt(
        (o_pos["x"] - h1_pos["x"]) ** 2
        + (o_pos["y"] - h1_pos["y"]) ** 2
        + (o_pos["z"] - h1_pos["z"]) ** 2
    )
    d_diff = dch - doh

    return c_pos, o_pos, h1_pos, l_x, l_y, d_diff


def calculate_reactive_flux_parameters(
    trajfile: str | Path, dt: float = 0.5
) -> tuple[Optional[np.ndarray], Optional[float]]:
    """Calculates the reaction coordinate and its initial time derivative.

    The reaction coordinate is the difference between the C-H1 and O-H1
    distances for each frame in the trajectory. The initial derivative is
    estimated with the three-point forward-difference formula:

    ``s'(0) = (-3s[0] + 4s[1] - s[2]) / (2 * dt)``

    Args:
        trajfile: Path to the XYZ trajectory file.
        dt: Time between consecutive trajectory frames. Must be positive.

    Returns:
        A tuple containing the reaction-coordinate array and its initial
        derivative. Returns ``(None, None)`` when the trajectory is invalid
        or contains fewer than three frames.

    Raises:
        ValueError: If ``dt`` is not positive.
    """
    if dt <= 0:
        raise ValueError("dt must be positive.")

    _, _, _, _, _, s = process_traj(trajfile, cutoff=0)

    if s is None or len(s) < 3:
        return None, None

    sdot_0 = (-3 * s[0] + 4 * s[1] - s[2]) / (2 * dt)

    return s, float(sdot_0)


def satisfies_rc_condition(pos: np.ndarray, vel: np.ndarray) -> bool:
    """Checks whether atom 3 increases the reaction coordinate.

    The reaction coordinate is defined as ``q = |r3 - r2| - |r3 - r1|``.
    This function evaluates its instantaneous derivative using the velocity
    of atom 3 and returns whether ``dq/dt`` is positive.

    Args:
        pos: Cartesian positions with shape ``(n_atoms, 3)``. The first three
            rows correspond to atoms 1, 2, and 3, respectively.
        vel: Cartesian velocities with shape ``(n_atoms, 3)``. The third row
            contains the velocity of atom 3.

    Returns:
        ``True`` if the reaction coordinate is increasing, otherwise ``False``.
    """
    r1, r2, r3 = pos[0], pos[1], pos[2]
    v3 = vel[2]

    # Unit vectors from atoms 1 and 2 toward atom 3.
    e13 = (r3 - r1) / np.linalg.norm(r3 - r1)
    e23 = (r3 - r2) / np.linalg.norm(r3 - r2)

    dq_dt = np.dot(e23 - e13, v3)
    return bool(dq_dt > 0)