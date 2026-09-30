import os
from pathlib import Path
from typing import Callable, Optional
import numpy as np

PathType = str | Path
FluxParamCallable = Callable[
    [PathType, float], tuple[Optional[np.ndarray], Optional[float]]
]

__provides__ = {"calculate_reactive_flux": "calculate_reactive_flux", "calculate_reactive_flux_error":"calculate_reactive_flux_with_propagated_error"}


def calculate_reactive_flux_for_trajectory(
    s: np.ndarray, sdot_0: float
) -> tuple[np.ndarray, float]:
    """Calculates the time-dependent reactive flux contribution for a single trajectory.

    Applies the Heaviside step function Theta(s(t)) to the 1-D reaction coordinate trajectory
    and scales it by the initial velocity along the coordinate. Trajectories starting with
    a non-positive velocity (sdot_0 <= 0) do not contribute to positive flux.

    Args:
        s (np.ndarray): Time series array of the 1-D reaction coordinate s(t) along the
            trajectory. Values s > 0 correspond to the product state, and s <= 0 to the
            reactant state.
        sdot_0 (float): Initial velocity sdot(0) along the reaction coordinate at t = 0.

    Returns:
        tuple[np.ndarray, float]: A tuple containing:
            - reactive_flux (np.ndarray): Time-dependent flux contribution sdot(0) * h(s(t)).
            Returns an array of zeros if sdot_0 <= 0.
            - initial_velocity_weight (float): Positive initial velocity contribution
            (sdot_0 if sdot_0 > 0, else 0.0).
    """
    if sdot_0 <= 0:
        return np.zeros_like(s, dtype=float), 0.0

    characteristic_function = (s > 0).astype(float)
    return sdot_0 * characteristic_function, float(sdot_0)


def calculate_reactive_flux(
    trajdir: PathType,
    reactive_flux_parameters: FluxParamCallable,
    dt: float = 0.5,
) -> Optional[np.ndarray]:
    """Computes the normalized time-dependent reactive flux kappa(t) across trajectory ensembles.

    Iterates through trajectory files in `trajdir`, projects each onto a 1-D reaction
    coordinate via `reactive_flux_parameters`, and calculates the ensemble-averaged
    reactive flux normalized by the positive initial velocity flux.

    Args:
        trajdir (PathType): Path to the directory containing trajectory data files.
        reactive_flux_parameters (FluxParamCallable): Function that accepts a trajectory
            file path and timestep `dt`, returning a tuple `(s, sdot_0)` containing the
            reaction coordinate trajectory s(t) and initial velocity sdot(0). Should
            return `(None, None)` if the trajectory is invalid.
        dt (float, optional): Time step or sampling interval passed to
            `reactive_flux_parameters`. Defaults to 0.5 fs.

    Returns:
        Optional[np.ndarray]: Array representing the normalized reactive flux kappa(t)
        across time steps, or None if no valid reactive trajectories were processed.

    Raises:
        FileNotFoundError: If `trajdir` does not exist or is not a directory.
    """
    dir_path = Path(trajdir)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Trajectory directory not found: {trajdir}")

    reactive_flux_numerator: Optional[np.ndarray] = None
    reactive_flux_denominator: float = 0.0

    for trajfile in sorted(dir_path.iterdir()):
        if not trajfile.is_file():
            continue

        s, sdot_0 = reactive_flux_parameters(trajfile, dt)
        if s is None or sdot_0 is None:
            continue

        flux_traj, v_0 = calculate_reactive_flux_for_trajectory(s, sdot_0)

        if reactive_flux_numerator is None:
            reactive_flux_numerator = flux_traj.copy()
            reactive_flux_denominator = v_0
        else:
            reactive_flux_numerator += flux_traj
            reactive_flux_denominator += v_0

    if reactive_flux_numerator is None or reactive_flux_denominator == 0.0:
        return None

    return reactive_flux_numerator / reactive_flux_denominator

def calculate_reactive_flux_error(
    trajdir: str, 
    reactive_flux_parameters: FluxParamCallable,
    dt: float = 0.5, 
    method: str = "bootstrap", 
    n_bootstraps: int = 5000
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates reactive flux kappa(t) and its standard error across trajectories.

    Parameters
    ----------
    trajdir : str
        Directory containing trajectory xyz files.
    dt : float
        Time step size.
    method : str
        'bootstrap' for non-parametric resampling or 'delta' for ratio-error
        propagation.
    n_bootstraps : int
        Number of resamples if method='bootstrap'.

    Returns
    -------
    kappa : np.ndarray
        Mean reactive flux profile over time.
    kappa_err : np.ndarray
        Standard error in kappa at each time step.
    """
    trajs = sorted(os.listdir(trajdir))

    num_list = []  # Stores A_i(t) = sdot_0 * theta(s(t)) for each trajectory
    den_list = []  # Stores B_i = max(0, sdot_0) for each trajectory

    for trajname in trajs:
        trajfile = os.path.join(trajdir, trajname)
        s, sdot_0 = reactive_flux_parameters(trajfile, dt)
        if s is None or sdot_0 is None:
            continue

        flux_i, v_0 = calculate_reactive_flux_for_trajectory(s, sdot_0)
        num_list.append(flux_i)
        den_list.append(v_0)

    if not num_list:
        return np.array([]), np.array([])

    A = np.array(num_list)  # Shape: (N_trajectories, N_timesteps)
    B = np.array(den_list)  # Shape: (N_trajectories,)
    N = len(B)

    if method == "bootstrap":
        boot_kappas = np.zeros((n_bootstraps, A.shape[1]))
        rng = np.random.default_rng()

        for b in range(n_bootstraps):
            indices = rng.choice(N, size=N, replace=True)
            denom_sum = np.sum(B[indices])
            if denom_sum > 0:
                boot_kappas[b] = np.sum(A[indices], axis=0) / denom_sum

        kappa = np.mean(boot_kappas, axis=0)
        kappa_err = np.std(boot_kappas, axis=0)

    elif method == "delta":
        mean_A = np.mean(A, axis=0)
        mean_B = np.mean(B)

        if mean_B == 0:
            return np.zeros(A.shape[1]), np.zeros(A.shape[1])

        kappa = mean_A / mean_B

        # Sample variances and covariance for ratio error propagation
        var_A = np.var(A, axis=0, ddof=1)
        var_B = np.var(B, ddof=1)
        cov_AB = (
            np.mean((A - mean_A) * (B[:, None] - mean_B), axis=0)
            * N
            / (N - 1)
        )

        # Delta method variance formula for ratio R = A / B
        var_kappa = (1 / (N * mean_B**2)) * (
            var_A + (kappa**2) * var_B - 2 * kappa * cov_AB
        )
        kappa_err = np.sqrt(np.maximum(0, var_kappa))

    else:
        raise ValueError("Method must be 'bootstrap' or 'delta'")

    return kappa, kappa_err
