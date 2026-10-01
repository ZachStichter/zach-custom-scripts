import os
import shutil
from pathlib import Path
import numpy as np
import ase.io
import ase.units
import ase.atoms
import ase.data
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from typing import Callable
from customscripts import write_ipi_velocity_xyz

__provides__ = {
    "generate_velocities":"generate_bennett_chandler_initial_velocities"
}


def check_ase_config():
    """Registers the custom ``L`` species required by the simulations.

    Adds ``L`` as the CavMD photon species to ASE's atomic-number,
    atomic-name, mass, covalent-radius, and van der Waals-radius tables when
    it is not already registered. The ASE atoms module's mass-table reference
    is updated as well so that ``Atoms.get_masses()`` recognizes the new
    species.

    This function is safe to call repeatedly; it leaves the ASE configuration
    unchanged when ``L`` is already registered.
    """
    if "L" not in ase.data.atomic_numbers:
        # Assign it the next available atomic number
        new_z = len(ase.data.chemical_symbols)
        ase.data.chemical_symbols.append("L")
        ase.data.atomic_numbers["L"] = new_z
        
        # Append to lists
        ase.data.atomic_names.append("CavMD_Photon")
        
        # Append to arrays in ase.data
        ase.data.atomic_masses = np.append(ase.data.atomic_masses, 1.0)
        ase.data.covalent_radii = np.append(ase.data.covalent_radii, 0.0)
        ase.data.vdw_radii = np.append(ase.data.vdw_radii, 0.0)
        
        # CRITICAL FIX: Update the local array references inside ase.atoms 
        # so that atoms.get_masses() uses the expanded 120-element array.
        ase.atoms.atomic_masses = ase.data.atomic_masses # type: ignore

def generate_velocities(
    simulation_directories: list[str] | list[os.PathLike],
    check_velocity: Callable[[np.ndarray, np.ndarray], bool],
    temperature_K: float = 300.0,
    n_independent_velocities: int = 1,
):
    """Generates and writes accepted Maxwell-Boltzmann velocity samples.

    Searches each directory for ``simulation.pos_c_<index>.xyz`` files,
    samples velocities at the requested temperature, and resamples
    until ``check_velocity`` accepts them. When two ``L`` atoms are present,
    their velocities are constrained to the x and y polarization directions,
    respectively. Accepted velocities are written as i-PI-compatible files
    named ``simulation.vel_c_<index>.xyz``. For each input file, multiple
    independent samples use indices offset by the total number of input files;
    the corresponding position file is copied to each additional index.

    Existing velocity files, non-directories, and unrelated XYZ files are
    skipped. Output indices are assigned globally in discovery order, starting
    at zero, so they remain continuous across the supplied directories.

    Args:
        simulation_directories: Directories containing input XYZ files.
        check_velocity: Predicate receiving atomic positions and sampled
            velocities. Sampling continues until it returns ``True``.
        temperature_K: Temperature in Kelvin used for Maxwell-Boltzmann
            velocity sampling. Defaults to ``300.0``.
        n_independent_velocities: Number of accepted velocity samples to
            generate for each input file. Defaults to ``1``.

    Returns:
        None.

    Raises:
        ValueError: If ``n_independent_velocities`` is less than one.
    """
    if n_independent_velocities < 1:
        raise ValueError("n_independent_velocities must be at least 1.")

    check_ase_config()
    input_files = []
    for dir_path in simulation_directories:
        folder = Path(dir_path)
        if not folder.is_dir():
            continue

        position_files = []
        for file_path in folder.glob("simulation.pos_c_*.xyz"):
            suffix = file_path.stem.rsplit("_", 1)[-1]
            if suffix.isdigit():
                position_files.append((int(suffix), file_path))

        input_files.extend(
            (folder, file_path)
            for _, file_path in sorted(position_files, key=lambda item: item[0])
        )

    total_input_files = len(input_files)
    for input_idx, (folder, file_path) in enumerate(input_files):

        atoms = ase.io.read(file_path)
        symbols = atoms.get_chemical_symbols() # type: ignore
        pos = atoms.get_positions() # type: ignore

        l_indices = [i for i, sym in enumerate(symbols) if sym == "L"]
        
        if len(l_indices) >= 2:
            idx_L1 = l_indices[0] # x-polarization
            idx_L2 = l_indices[1] # y-polarization
        else:
            idx_L1 = idx_L2 = None

        for sample_idx in range(n_independent_velocities):
            while True:
                MaxwellBoltzmannDistribution(atoms, temperature_K=temperature_K)  # type: ignore
                vel = atoms.get_velocities()  # type: ignore

                if idx_L1 is not None and idx_L2 is not None:
                    vel[idx_L1] = np.array([vel[idx_L1, 0], 0.0, 0.0])
                    vel[idx_L2] = np.array([0.0, vel[idx_L2, 1], 0.0])

                if check_velocity(pos, vel):
                    break

            output_idx = input_idx + sample_idx * total_input_files
            if sample_idx > 0:
                position_stem = file_path.stem.rsplit("_", 1)[0]
                position_file = folder / (
                    f"{position_stem}_{output_idx}{file_path.suffix}"
                )
                shutil.copy2(file_path, position_file)

            # Write the velocities exactly as i-PI expects them.
            output_file = folder / f"simulation.vel_c_{output_idx}.xyz"
            write_ipi_velocity_xyz(output_file, symbols, vel)