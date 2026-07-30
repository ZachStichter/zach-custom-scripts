from .read_xyz import read_xyz
import numpy as np
from numpy.typing import ArrayLike
from typing import Tuple
from os import PathLike

__provides__ = {
    'process_traj': 'xyz_to_1d_formaldehyde_order_parameter'
}

def process_traj(trajfile:str|PathLike)->Tuple[ArrayLike, ArrayLike,ArrayLike, ArrayLike]|Tuple[None,None,None,None]:
    """
    Provided a CavMD formaldehyde trajectory file, returns the following order parameters:
    l_pos: Photonic polarization, defined as the X- and Y- components of the photonic position variable
    d_diff: difference between the C-H bond length and the O-H bond length
    dch: C-H bond length (reactive proton, H1)
    doh: O-H bond length (reactive proton, H1)

    Args:
        trajfile (str|PathLike): variable signifying a path to the xyz trajectory to process

    Returns:
        A tuple containing (l_pos, d_diff, dch, doh) as specified above.
    """
    traj1 = read_xyz(trajfile)
    if traj1 == {}:
        return (None, None, None, None)

    lookup  = {0:'c', 1:'o', 2:'h', 3:'h'}

    # positions output in ANGSTROMS
    c_pos = traj1[0]
    o_pos = traj1[1]
    h1_pos = traj1[2]
    h2_pos = traj1[3]
    l_pos = np.sqrt(traj1[4]['x']**2+traj1[5]['y']**2)

    dch = np.sqrt((c_pos['x']-h1_pos['x'])**2+(c_pos['y']-h1_pos['y'])**2+(c_pos['z']-h1_pos['z'])**2)
    doh = np.sqrt((o_pos['x']-h1_pos['x'])**2+(o_pos['y']-h1_pos['y'])**2+(o_pos['z']-h1_pos['z'])**2)
    d_diff = (dch-doh)


    return l_pos, d_diff, dch, doh