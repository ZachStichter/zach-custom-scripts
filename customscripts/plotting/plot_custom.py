import matplotlib.pyplot as plt

__provides__ = {}


def plot_customized_matplotlib(
    x=None,
    y=None,
    plot_type=None,
    use_existing=None,
    return_obj=None,
    save=None,
    save_path=None,
    show=None,
    title=None,
    xlabel=None,
    ylabel=None,
    data_label=None,
    show_data_label=None,
    figure_layout=None,
    figure_size=None,
    share_x=None,
    share_y=None,
    aspect=None,
    polar=None,
    xlims=None,
    ylims=None,
    x_scale=None,
    y_scale=None,
    frame_on=None,
    grid=None,
    line_alpha=None,
    line_color=None,
    line_style=None,
    line_width=None,
    marker=None,
    marker_color=None,
    marker_size=None,
    marker_every=None,
):
    """
    Master-function for creating figures. Wraps matplotlib.pyplot.

    Args:
        ## DATA ##
            x (None|Iterable): the x-data
            y (None|Iterable): the y-data (REQUIRED)

        ## PLOT ADMINISTRATION ##
            plot_type (None|Literal['plot','scatter']): use the provided matplotlib plot type. If None, default to 'plot'
            use_existing (None|Tuple[Fig, Ax]): if not None, use the provided fig, ax as the figure entry point
            return_obj (None|bool): if True, return the fig, ax for later use
            save (None|bool): if True, save the figure
            save_path (None|PathLike|str): when saving the figure, save it here. If None, default to ./fig.png
            show (None|bool): if True, show the figure using the matplotlib built-in figure renderer

        ## TITLES AND LABELS ##
            title (None|str): the user-readable axis title
            xlabel (None|str): the user-readable x-axis title
            ylabel (None|str): the user-readable y-axis title
            data_label (None|str): the user-readable label to be written in the legend
            show_data_label (None|bool): if True, show the user label on the legend

        ## SIZES AND LAYOUTS ##
            figure_layout (None|Literal['constrained', 'compressed', 'tight', 'none']): specify the figure layout. See matplotlib docs for more
            figure_size (None|Tuple[float, float]): specify the figure size in inches. Default is 6.4"x4.8"
            share_x (None|matplotlib.axes): share the x-axis with another axes object
            share_y (None|matplotlib.axes): share the y-axis with another axes object
            aspect (None|Literal['auto','equal']|float): specify the aspect ratio for the plot
            polar (None|bool): if true, configure the plot to use polar coordinate style. x --> theta, y --> r
            x_scale (None|Literal['linear', 'log']): configure the x-axis to use linear or logarithmic scale
            y_scale (None|Literal['linear', 'log']): configure the y-axis to use linear or logarithmic scale
            frame_on (None|bool): if False, disable the axis outer rectangle frame
            grid (None|Dict[Any]): if present, set the grid parameters using key=value to ax.grid().
                                   See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html#matplotlib.pyplot.grid

        ## LINE PARAMETERS ##
            line_alpha (None|float[0,1]): if provided, set the alpha of the line to the value. Note: alpha must be on the range [0,1]
            line_color (None|
                        Tuple[float,float,float]|
                        Tuple[float,float,float,float]|
                        str|
                        Literal['b','g','r','c','m','y','k','w']|
                        Literal['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7']|
                        Tuple[previous, float]
                        ): Aigt, this one's a mess. See https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def
            line_style (None|
                       Literal['-','--','-.',':','']|
                       Tuple[float,Tuple[float,float]]
                       ): another mess. See https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linestyle
            line_width (None|float): line width, in points

        ## MARKER PARAMETERS ##
            marker (None|str|int|Tuple[int,int,float]|MarkerStyle): if None, no marker. See https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
            marker_color (misc.): see line_color.
            marker_size (None|float): marker size in points
            marker_every (None|
                          int|
                          Tuple[int,int]|
                          Tuple[int,int,int]|
                          list[int]|
                          list[float]|
                          float|
                          Tuple[float,float]): see https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_markevery

    """
    ### SHORT CIRCUIT IF NO DATA IS PROVIDED ###
    try:
        assert y is not None
    except AssertionError:
        raise ValueError("Cannot plot with no y-data!")

    ### SET UP MAPPINGS FOR LATER USE ###
    ### MAKE SURE TO REGISTER MAPPINGS AS FEATURES ARE ADDED ###

    args_param_map = {
        "figure_size": "figsize",
        "figure_layout": "layout",
        "share_x": "sharex",
        "share_y": "sharey",
        "frame_on": "frameon",
    }

    plot_param_map = {
        "line_alpha": "alpha",
        "line_color": "color",
        "line_style": "linestyle",
        "line_width": "linewidth",
        "marker": "marker",
        "marker_size": "markersize",
        "marker_every": "markevery",
        "data_label": "label",
    }

    scatter_param_map = {
        "marker_color": "c",
        "marker": "marker",
        "marker_size": "s",
        "data_label": "label",
    }

    axis_method_map = {
        "title": "set_title",
        "xlabel": "set_xlabel",
        "ylabel": "set_ylabel",
        "xlims": "set_xlim",
        "ylims": "set_ylim",
        "x_scale": "set_xscale",
        "y_scale": "set_yscale",
        "aspect": "set_aspect",
    }

    ### FILTER PARAMETERS TO FIND USED VALUES ###
    params = locals()
    used_args = {k: v for k, v in params.items() if v is not None}
    keys = used_args.keys()  # keys for easy lookup

    args_dict = {}
    for arg in ["share_x", "share_y", "figure_size", "frame_on", "figure_layout"]:
        alias = args_param_map.get(arg, arg)  #
        if arg in keys:
            print(args_dict[alias])
            print(used_args[arg])
            args_dict[alias] = used_args[arg]

    if "polar" in keys:
        args_dict["subplot_kw"] = {"polar": used_args["polar"]}

    if "use_existing" in keys:
        fig, ax = used_args["use_existing"]
    else:
        fig, ax = plt.subplots(**args_dict)

    if "grid" in keys:
        ax.grid(**used_args["grid"])

    plot_type = used_args.get("plot_type", "plot")
    plot_kwargs = {}

    if plot_type.lower() == "plot":
        for arg_key, mpl_key in plot_param_map.items():
            if arg_key in keys:
                plot_kwargs[mpl_key] = used_args[arg_key]

        if "marker_color" in keys:
            plot_kwargs["mfc"] = used_args["marker_color"]

        if x is not None:
            ax.plot(x, y, **plot_kwargs)
        else:
            ax.plot(y, **plot_kwargs)

    elif plot_type.lower() == "scatter":
        for arg_key, mpl_key in scatter_param_map.items():
            if arg_key in keys:
                plot_kwargs[mpl_key] = used_args[arg_key]

        if x is not None:
            ax.scatter(x, y, **plot_kwargs)
        else:
            ax.scatter(list(range(len(y))), y, **plot_kwargs)

    else:
        raise NotImplementedError(f"Unknown plot type {plot_type}. Try again or add!")

    for arg_key, method in axis_method_map.items():
        if arg_key in keys:
            getattr(ax, method)(used_args[arg_key])

    if used_args.get("show_data_label", False):
        ax.legend()

    if used_args.get("save", False):
        save_path = used_args.get("save_path", "./fig.png")
        fig.savefig(save_path)

    if used_args.get("show", False) and used_args.get("return_obj", True):
        plt.show(block=False)

    if used_args.get("return_obj", False):
        return fig, ax
