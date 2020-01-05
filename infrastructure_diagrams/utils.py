import json
import operator
import os
import magic
import yaml
from pprint import pprint
from queue import Queue
from pprint import pprint
from SecretColors import Palette
from functools import reduce
from .color import darken_color, lighten_color
from .enums import ComponentType

from graphviz import Digraph
from .settings import (
    DEFAULT_EDGE_ATTRIBUTES,
    DEFAULT_NODE_ATTRIBUTES,
    IGNORE_EDGE_ATTRIBUTES,
    IGNORE_GROUP_ATTRIBUTES,
    IGNORE_NODE_ATTRIBUTES,
)


def parse_json(path):
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except json.decoder.JSONDecodeError:
        return None


def parse_yaml(path):
    with open(path) as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.SafeLoader)


def split_into_rows(data, columns):
    return [data[i : i + columns] for i in range(0, len(data), columns)]


def set_random_primary_colors(groups):
    p = Palette("material")
    random_colors = p.random(no_of_colors=len(groups))
    i = 0
    for group in groups:
        if "color" in group or (
            "custom_attributes" in group
            and "primary_color" in group["custom_attributes"]
        ):
            continue
        custom_attributes = {}
        if "custom_attributes" in group:
            custom_attributes = group["custom_attributes"]

        custom_attributes["primary_color"] = random_colors[i]
        group["custom_attributes"] = custom_attributes
        i += 1


def load_diagram(path):
    if not os.path.isfile(path):
        print("ERROR:", f"Could not find file: {path}")
        exit(1)

    mimetype = magic.from_file(path, mime=True)
    if mimetype != "text/plain":
        print("ERROR:", f"File mimetype is not text/plain: {mimetype}")
        exit(1)

    config = parse_json(path)
    if config is None:
        config = parse_yaml(path)

    if config is None:
        print("ERROR:", f"Could not parse the diagram file as YAML or ISON")
        exit(1)

    # TODO: add schema validation

    return config


def generate_label(attributes, component_type):
    label = ""
    if "label" in attributes:
        label = attributes["label"]
    elif "title" in attributes or "subtitle" in attributes:
        title_fontsize = attributes.get("title_fontsize", 20)
        subtitle_fontsize = attributes.get("subtitle_fontsize", 10)

        label = "<"
        if "title" in attributes:
            if component_type == ComponentType.GROUP:
                label += f"<br/><font point-size='{title_fontsize}'><b><u>{attributes['title']}</u></b></font>"
            else:
                label += f"<font point-size='{title_fontsize}'><b>{attributes['title']}</b></font>"

        if "subtitle" in attributes:
            if component_type == ComponentType.NODE:
                label += "<br/>"

            label += f"<br/><font point-size='{subtitle_fontsize}'><i>{attributes['subtitle']}</i></font>"

        label += ">"

    if label != "":
        attributes["label"] = label


def parse_custom_attributes(kwargs, component_type, custom_attributes):
    # TODO: Convert all the custom attributes and kwargs to strings

    # General attributes
    if "primary_color" in custom_attributes:
        primary_color = custom_attributes["primary_color"]
        if component_type == ComponentType.GROUP and "color" not in kwargs:
            kwargs["color"] = primary_color
            kwargs["fontcolor"] = primary_color
            kwargs["bgcolor"] = lighten_color(primary_color, 185)
        elif component_type == ComponentType.NODE and "color" not in kwargs:
            kwargs["style"] = "filled"
            kwargs["fillcolor"] = lighten_color(primary_color)
            kwargs["color"] = primary_color
        elif component_type == ComponentType.EDGE and "color" not in kwargs:
            kwargs["color"] = primary_color
            kwargs["fontcolor"] = primary_color

    if component_type == ComponentType.NODE and "nodes" in custom_attributes:
        # Handle custom attributes for nodes
        attributes = custom_attributes["nodes"].copy()

        # Parse node color
        if "color" in attributes and "color" not in kwargs:
            # Sets the node background color and fades the border to a darker
            # color
            color = attributes["color"]
            kwargs["style"] = "filled"
            kwargs["fillcolor"] = color
            kwargs["color"] = str(darken_color(color))
            del attributes["color"]

        if "border_width" in attributes and "penwidth" not in kwargs:
            kwargs["penwidth"] = attributes["border_width"]
            del attributes["border_width"]

        kwargs = {**kwargs, **attributes}

    elif component_type == ComponentType.GROUP and "groups" in custom_attributes:
        # Handle custom attributes for groups
        attributes = custom_attributes["groups"].copy()

        # Parse border color
        if "border_color" in attributes and "color" not in kwargs:
            kwargs["color"] = str(attributes["border_color"])
            del attributes["border_color"]
        if "border_type" in attributes and "style" not in kwargs:
            kwargs["style"] = attributes["border_type"]
            del attributes["border_type"]
        if "border_width" in attributes and "penwidth" not in kwargs:
            kwargs["penwidth"] = attributes["border_width"]
            del attributes["border_width"]

        kwargs = {**kwargs, **attributes}
    elif component_type == ComponentType.EDGE and "edges" in custom_attributes:
        # Handle custom attributes for edges
        attributes = custom_attributes["edges"].copy()

        if "width" in attributes and "penwidth" not in kwargs:
            kwargs["penwidth"] = str(attributes["width"])
            del attributes["width"]

        kwargs = {**kwargs, **attributes}

    return kwargs


def add_global_nodes(global_graph, group, custom_attributes):
    group["nodes"] = group["global_nodes"]
    add_nodes(global_graph, global_graph, group, custom_attributes)


def add_nodes(global_graph, graph, group, custom_attributes):
    max_nodes_per_row = None
    if "max_nodes_per_row" in group:
        # To split nodes into rows we need to add invisible edges.
        max_nodes_per_row = group["max_nodes_per_row"]
        node_rows = split_into_rows(group["nodes"], columns=max_nodes_per_row)

    a = 4
    for node in group["nodes"]:
        if max_nodes_per_row and len(group["nodes"]) > a:
            edge = {"node": group["nodes"][a]["id"], "style": "invis"}
            if "edges" in node:
                node["edges"].append(edge)
            else:
                node["edges"] = [edge]
            a += 1

        node_kwargs = DEFAULT_NODE_ATTRIBUTES.copy()

        # Check for custom settings
        if "custom_attributes" in node:
            custom_attributes = {**custom_attributes, **node["custom_attributes"]}

        node_kwargs = parse_custom_attributes(
            node_kwargs, ComponentType.NODE, custom_attributes
        )

        # Check for node graphviz attributes
        for key in node.keys():
            if key in IGNORE_NODE_ATTRIBUTES:
                continue
            node_kwargs[key] = str(node[key])

        generate_label(node_kwargs, ComponentType.NODE)

        graph.node(node["id"], **node_kwargs)

        # Check if the node has an edge, add the edge to the global graph if so.
        if "edges" in node:
            for edge in node["edges"]:
                edge_kwargs = DEFAULT_EDGE_ATTRIBUTES.copy()

                # Check for custom settings
                if "custom_attributes" in edge:
                    custom_attributes = {
                        **custom_attributes,
                        **edge["custom_attributes"],
                    }

                edge_kwargs = parse_custom_attributes(
                    edge_kwargs, ComponentType.EDGE, custom_attributes
                )

                for key in edge.keys():
                    if key in IGNORE_EDGE_ATTRIBUTES:
                        continue
                    edge_kwargs[key] = str(edge[key])

                global_graph.edge(node["id"], edge["node"], **edge_kwargs)


def create_group_graph(global_graph, group, custom_attributes):
    group_graph = Digraph(name=f"cluster_{group['id']}")

    # Check for custom settings
    if "custom_attributes" in group:
        custom_attributes = {**custom_attributes, **group["custom_attributes"]}

    group = parse_custom_attributes(group, ComponentType.GROUP, custom_attributes)
    generate_label(group, ComponentType.GROUP)

    for key in group.keys():
        if key in IGNORE_GROUP_ATTRIBUTES:
            continue
        group_graph.attr(**{key: str(group[key])})

    if "nodes" in group:
        add_nodes(global_graph, group_graph, group, custom_attributes)

    return group_graph


def map_groups_children(groups):
    group_children = {}
    for group in groups:
        group_id = group["id"]
        if "parent_group" in group:
            parent_group = group["parent_group"]
            group_children.setdefault(parent_group, set()).add(group_id)

        group_children[group_id] = group_children.get(group_id, set())
    return group_children


def add_groups(global_graph, groups, custom_attributes):
    groups_children = map_groups_children(groups)
    group_graphs = {}
    queue = Queue()

    # Add all the groups to the queue.
    for group in groups:
        group_id = group["id"]
        group_graphs[group_id] = create_group_graph(
            global_graph, group, custom_attributes
        )
        queue.put(group)

    """
    Go through the queue and check if group has children (`groups_children`, i.e. sub-groups).
    If the group has children:
        - Check if each child has been processed already (they exists in processed_groups).
        - If one of the children have not been processed, add the group back
          into the queue.
    If all the children have been processed (or the group has no children), add the group
    graph to the parent group graph. If the group has no parent, add it to the global graph.
    """
    processed_groups = set()
    while not queue.empty():
        group = queue.get()
        group_id = group["id"]
        group_children = groups_children[group_id]

        # Check if ALL of the children have been processed.
        if group_children.issubset(processed_groups):
            processed_groups.add(group_id)
            if "parent_group" not in group:
                global_graph.subgraph(group_graphs[group_id])
            else:
                parent_id = group["parent_group"]
                parent_graph = group_graphs[parent_id]
                group_graphs[parent_id].subgraph(group_graphs[group_id])
        else:
            """
            Some children of the group have not been processed yet.
            Add the group back to the queue.
            """
            queue.put(group)
