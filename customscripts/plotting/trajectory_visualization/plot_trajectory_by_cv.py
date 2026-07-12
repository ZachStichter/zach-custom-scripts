from customscripts import read_xyz
from collections.abc import Callable
from customscripts.plotting.plot_custom import plot_customized_matplotlib

__provides__ = {
    "show_trajectory_by_two_dimensional_cv": "two_d_cv_show_traj",
    "export_trajectory_by_two_dimensional_cv": "two_d_cv_export_traj",
    "show_export_trajectory_by_two_dimensional_cv": "two_d_cv_show_export_traj",
}


def show_trajectory_by_two_dimensional_cv(
    input_file, input_file_type, cv1_idx, cv1_label, cv2_idx, cv2_label, cv_func
):
    """
    Display a matplotlib graph containing a trajectory.

    Args:
        input_file (str|PathLike): the file to read
        input_file_type (Literal['xyz', 'ipi_out']): the type structure used to parse the input file
        cv1_idx (int): the 0-indexed position of the first CV value
        cv1_label (str): the x-axis title corresponding to CV1
        cv2_idx (int): the 0-indexed position of the second CV value
        cv2_label (str): the y-axis title corresponding to CV2
        cv_func (Callable): any function definition accepting arguments of the form (x_1, y_1, z_1, x_2, y_2, z_2)
                            and returning a Tuple containing two equal-length datasets, which are the CVs proper
    """
    cv1, cv2 = _get_cv_content(input_file, input_file_type, cv1_idx, cv2_idx, cv_func)

    _plot_trajectory_by_cv(cv1, cv2, cv1_label, cv2_label, show=True)


def export_trajectory_by_two_dimensional_cv(
    input_file,
    input_file_type,
    output_file,
    cv1_idx,
    cv1_label,
    cv2_idx,
    cv2_label,
    cv_func:Callable,
):
    """
    Save a matplotlib graph containing a trajectory.

    Args:
        input_file (str|PathLike): the file to read
        input_file_type (Literal['xyz', 'ipi_out']): the type structure used to parse the input file
        cv1_idx (int): the 0-indexed position of the first CV value
        cv1_label (str): the x-axis title corresponding to CV1
        cv2_idx (int): the 0-indexed position of the second CV value
        cv2_label (str): the y-axis title corresponding to CV2
        cv_func (Callable): any function definition accepting arguments of the form (x_1, y_1, z_1, x_2, y_2, z_2)
                            and returning a Tuple containing two equal-length datasets, which are the CVs proper
    """
    cv1, cv2 = _get_cv_content(input_file, input_file_type, cv1_idx, cv2_idx, cv_func)

    _plot_trajectory_by_cv(
        cv1, cv2, cv1_label, cv2_label, save=True, save_path=output_file
    )


def show_export_trajectory_by_two_dimensional_cv(
    input_file,
    input_file_type,
    output_file,
    cv1_idx,
    cv1_label,
    cv2_idx,
    cv2_label,
    cv_func,
):
    """
    Save a matplotlib graph containing a trajectory.

    Args:
        input_file (str|PathLike): the file to read
        input_file_type (Literal['xyz', 'ipi_out']): the type structure used to parse the input file
        cv1_idx (int): the 0-indexed position of the first CV value
        cv1_label (str): the x-axis title corresponding to CV1
        cv2_idx (int): the 0-indexed position of the second CV value
        cv2_label (str): the y-axis title corresponding to CV2
        cv_func (Callable): any function definition accepting arguments of the form (x_1, y_1, z_1, x_2, y_2, z_2)
                            and returning a Tuple containing two equal-length datasets, which are the CVs proper
    """
    cv1, cv2 = _get_cv_content(input_file, input_file_type, cv1_idx, cv2_idx, cv_func)

    _plot_trajectory_by_cv(
        cv1, cv2, cv1_label, cv2_label, show=True, save=True, save_path=output_file
    )


def _get_cv_content(input_file, input_file_type, cv1_idx, cv2_idx, cv_func):
    """
    Helper function to take in run-time variables and import CV data. Returns cv1, cv2 arrays.
    """
    registered_file_types = {
        "xyz": read_xyz,
    }

    try:
        assert input_file_type in registered_file_types
    except AssertionError:
        raise ValueError(
            f"Error displaying trajectory plot. Cannot yet process input file type {input_file_type}"
        )

    input_factory = registered_file_types[input_file_type]

    content = input_factory(input_file, [cv1_idx, cv2_idx])

    print(content)

    x_1 = content[cv1_idx]["x"]
    y_1 = content[cv1_idx]["y"]
    z_1 = content[cv1_idx]["z"]
    x_2 = content[cv2_idx]["x"]
    y_2 = content[cv2_idx]["y"]
    z_2 = content[cv2_idx]["z"]

    cv1, cv2 = cv_func(x_1, y_1, z_1, x_2, y_2, z_2)

    return cv1, cv2


def _plot_trajectory_by_cv(
    cv1, cv2, label1, label2, show=False, save=False, save_path=None
):
    if save + show == False:
        return
    else:
        plot_customized_matplotlib(
            cv1,
            cv2,
            xlabel=label1,
            ylabel=label2,
            show=show,
            save=save,
            save_path=save_path,
            marker=None,
        )
