import os

from graphviz import Digraph
from .settings import (
    COPYRIGHT_STRING,
    DEFAULT_GLOBAL_GRAPH_ATTRIBUTES,
    IGNORE_GRAPH_ATTRIBUTES,
)
from .utils import (
    add_global_nodes,
    add_groups,
    parse_custom_attributes,
    set_random_primary_colors,
)


def generate_graph(diagram, options={}):
    global_graph = Digraph()

    custom_attributes = {}
    if "custom_attributes" in diagram:
        custom_attributes = diagram["custom_attributes"]
        if (
            "groups" in diagram
            and "groups" in custom_attributes
            and "random_color" in custom_attributes["groups"]
        ):
            set_random_primary_colors(diagram["groups"])

    # Set global graph attributes
    graph_attributes = {}
    if "graph_attributes" in diagram:
        graph_attributes = diagram["graph_attributes"]

    graph_kwargs = DEFAULT_GLOBAL_GRAPH_ATTRIBUTES
    for key in graph_attributes:
        if key in IGNORE_GRAPH_ATTRIBUTES:
            continue
        graph_kwargs[key] = graph_attributes[key]

    if not ("disable_copyright" in diagram and diagram["disable_copyright"] is True):
        graph_kwargs["label"] += f"\n{COPYRIGHT_STRING}"

    for key, kwarg in graph_kwargs.items():
        global_graph.attr(**{key: str(kwarg)})

    if "global_nodes" in diagram:
        add_global_nodes(global_graph, diagram, custom_attributes)
    if "groups" in diagram:
        add_groups(global_graph, diagram["groups"], custom_attributes)

    output = options["output"].split(".")  # TODO: add argument?
    filename = output[0]
    format = output[1]

    saved_filename = global_graph.render(
        filename=filename, format=format, renderer=options["renderer"], cleanup=True
    )

    if options["display"]:
        global_graph.view(cleanup=True)

    os.rename(saved_filename, options["output"])
