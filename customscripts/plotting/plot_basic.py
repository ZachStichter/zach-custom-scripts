import numpy as np
from .plot_custom import plot_customized_matplotlib

__provides__ = {
    "export_basic_line_plot_matplotlib": "export_default_line_plot",
    "export_basic_scatter_plot_matplotlib": "export_default_scatter_plot",
    "display_basic_line_plot_matplotlib": "display_default_line_plot",
    "display_basic_scatter_plot_matplotlib": "display_default_scatter_plot",
}


def export_basic_line_plot_matplotlib(x, y, fpath):
    """
    Given a dataset, export a matplotlib line plot to fpath.

    Default implementation - no customization possible. Requires x and y data to have the same shape.

    If fpath doesn't end with '.png', it is added to the path.

    Args:
        x (list|np.array_like): the x-component of the data
        y (list|np.array_like): the y-component of the data
        fpath (str|os.PathLike): the output file path for saving the image
    """
    try:
        x = np.array(x)
        y = np.array(y)
        assert x.shape == y.shape
    except AssertionError:
        raise ValueError(
            f"x and y shapes must be identical! Found x: {x.shape} but y: {y.shape}"
        )
    except:
        print("Problem setting x and y as arrays. Verify types and try again.")
        return

    if not fpath.endswith(".png"):
        fpath = fpath + ".png"

    plot_customized_matplotlib(x, y, save=True, save_path=fpath)


def export_basic_scatter_plot_matplotlib(x, y, fpath):
    """
    Given a dataset, export a matplotlib scatter plot to fpath.

    Default implementation - no customization possible. Requires x and y data to have the same shape.

    If fpath doesn't end with '.png', it is added to the path.

    Args:
        x (list|np.array_like): the x-component of the data
        y (list|np.array_like): the y-component of the data
        fpath: the output file path for saving the image
    """
    try:
        x = np.array(x)
        y = np.array(y)
        assert x.shape == y.shape
    except AssertionError:
        raise ValueError(
            f"x and y shapes must be identical! Found x: {x.shape} but y: {y.shape}"
        )
    except:
        print("Problem setting x and y as arrays. Verify types and try again.")
        return

    if not fpath.endswith(".png"):
        fpath = fpath + ".png"

    plot_customized_matplotlib(x, y, plot_type="scatter", save=True, save_path=fpath)

def display_basic_line_plot_matplotlib(x, y):
    """
    Given a dataset, plot it on a line plot and display it.

    Default implementation - no customization possible. Requires x and y data to have the same shape.

    If fpath doesn't end with '.png', it is added to the path.

    Args:
        x (list|np.array_like): the x-component of the data
        y (list|np.array_like): the y-component of the data
    """
    try:
        x = np.array(x)
        y = np.array(y)
        assert x.shape == y.shape
    except AssertionError:
        raise ValueError(
            f"x and y shapes must be identical! Found x: {x.shape} but y: {y.shape}"
        )
    except:
        print("Problem setting x and y as arrays. Verify types and try again.")
        return

    plot_customized_matplotlib(x, y, show=True)


def display_basic_scatter_plot_matplotlib(x, y, hold=True):
    """
    Given a dataset, plot it on a scatter plot and display it.

    Default implementation - no customization possible. Requires x and y data to have the same shape.

    If fpath doesn't end with '.png', it is added to the path.

    Args:
        x (list|np.array_like): the x-component of the data
        y (list|np.array_like): the y-component of the data
    """
    try:
        x = np.array(x)
        y = np.array(y)
        assert x.shape == y.shape
    except AssertionError:
        raise ValueError(
            f"x and y shapes must be identical! Found x: {x.shape} but y: {y.shape}"
        )
    except:
        print("Problem setting x and y as arrays. Verify types and try again.")
        return

    plot_customized_matplotlib(x, y, plot_type="scatter", show=True)