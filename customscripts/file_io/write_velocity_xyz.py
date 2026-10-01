import numpy as np
from pathlib import Path
from ase.units import fs

__provides__ = {
    "write_ipi_velocity_xyz":"write_ipi_velocity_xyz"
}

def write_ipi_velocity_xyz(
    filepath: Path | str, symbols: list[str], velocities_ase: np.ndarray
) -> None:
    """Writes ASE velocities to an i-PI-compatible XYZ file.

    The velocity components are written as the three XYZ coordinate columns
    and converted from ASE's internal units to meters per second. The comment
    line identifies the values as ``velocity{m/s}``, which i-PI uses to
    interpret the columns correctly.

    Args:
        filepath: Destination path for the XYZ file.
        symbols: Atomic symbols in the same order as the velocity rows.
        velocities_ase: Array of ASE velocities with shape ``(n_atoms, 3)``.

    Raises:
        ValueError: If ``velocities_ase`` does not have three components per
            atom or if its number of rows differs from ``symbols``.
    """
    if velocities_ase.ndim != 2 or velocities_ase.shape[1] != 3:
        raise ValueError("velocities_ase must have shape (n_atoms, 3).")

    # Convert ASE internal velocity units to m/s.
    velocities_m_s = velocities_ase * fs * 1e5

    with Path(filepath).open("w", encoding="utf-8") as file:
        file.write(f"{len(symbols)}\n")
        file.write("velocity{m/s}\n")
        for symbol, velocity in zip(symbols, velocities_m_s, strict=True):
            file.write(
                f"{symbol:<5} {velocity[0]:>15.8f} "
                f"{velocity[1]:>15.8f} {velocity[2]:>15.8f}\n"
            )