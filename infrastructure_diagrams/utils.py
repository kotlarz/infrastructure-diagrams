import json
import operator
import os
from functools import reduce

import magic
import yaml

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


def get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def set_in_dict(data_dict, map_list, value):
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


# TODO: Find a more efficient way to do this. BFS? DFS?
def find_group(groups, find_group_id, group_path=[]):
    if find_group_id in groups.keys():
        group_path += [find_group_id, "children"]
        return group_path if len(group_path) > 0 else None

    # Loop through all the keys (group ID's) in the current group
    for group_id, group in groups.items():
        sub_path = group_path + [group_id, "children"]

        # Loop through all the children of the group and see if we can find our
        # group
        for child_id, child in group["children"].items():
            final_path = find_group({child_id: child}, find_group_id, sub_path)
            if final_path is not None:
                return final_path
    return


"""
Reverse traverse through the groups.
Graphviz requires the subgraph (inner group) to be created before adding it to
the parent graph (of the inner group).
"""


def reverse_tree(group, current=[]):
    if len(group["children"]) == 0:
        return current

    for child_id, child in group["children"].items():
        current.append({"id": child_id, "parent": child["parent_group"]})

    return current


def add_global_nodes(global_graph, nodes):
    add_nodes(global_graph, global_graph, nodes)


def add_nodes(global_graph, graph, nodes):
    for node in nodes:
        node_kwargs = DEFAULT_NODE_ATTRIBUTES.copy()
        for key in node.keys():
            if key in IGNORE_NODE_ATTRIBUTES:
                continue
            node_kwargs[key] = node[key]

        graph.node(node["id"], **node_kwargs)

        # Check if the node has an edge, add the edge to the global graph if so.
        if "edges" in node.keys():
            for edge in node["edges"]:
                edge_kwargs = DEFAULT_EDGE_ATTRIBUTES.copy()

                for key in edge.keys():
                    if key in IGNORE_EDGE_ATTRIBUTES:
                        continue
                    edge_kwargs[key] = edge[key]
                global_graph.edge(node["id"], edge["node"], **edge_kwargs)


"""
Map the groups into a tree, this is needed to create the graphs in reverse.
Example:

Pseudo input:
    - Group 1, Parent: None
    - Group 2, Parent: Group 1
    - Group 3, Parent: Group 2
    - Group 4, Parent: Group 2
    - Group 5, Parent: None
Pseduo output:
    - Group 1:
      Children:
        - Group2:
          Children:
            - Group 3:
              Children: None
            - Group 4:
              Children: None
    - Group 5:
      Children: None
"""


def map_group_tree(global_graph, groups):
    group_graphs = {}
    group_tree = {}
    queue = {}
    for group in groups:
        group["children"] = {}
        group_id = group["id"]

        g = Digraph(name=f"cluster_{group_id}")
        for key in group.keys():
            if key in IGNORE_GROUP_ATTRIBUTES:
                continue
            g.attr(**{key: str(group[key])})

        if "nodes" in group.keys():
            add_nodes(global_graph, g, group["nodes"])
        group_graphs[group_id] = g

        # Check if the group has a parent group, if not this group is a global group
        if "parent_group" not in group:
            group_tree[group_id] = group

            # Check if group exists in queue
            group_queue_path = find_group(queue, group_id, [])
            if group_queue_path:
                queue_group = get_from_dict(queue, group_queue_path)
                group_tree[group_id]["children"] = queue_group
                del queue[group_id]
            continue

        parent_group = group["parent_group"]

        # Check if parent exists in queue
        parent_queue_path = find_group(queue, parent_group, [])
        if parent_queue_path is not None:
            queue_parent = get_from_dict(queue, parent_queue_path)
            queue_parent[group_id] = group
            set_in_dict(queue, parent_queue_path, queue_parent)
            continue

        # Check if parent exists in tree
        parent_tree_path = find_group(group_tree, parent_group, [])
        if parent_tree_path is not None:
            tree_parent = get_from_dict(group_tree, parent_tree_path)
            tree_parent[group_id] = group
            set_in_dict(group_tree, parent_tree_path, tree_parent)
            continue

        # Check if group exists in queue
        group_queue_path = find_group(queue, group_id, [])
        if group_queue_path is not None:
            queue_group = get_from_dict(queue, group_queue_path)
            queue[parent_group] = {
                "children": {group_id: {**group, **{"children": queue_group}}}
            }
            del queue[group_id]
            continue

        if parent_group not in queue:
            queue[parent_group] = {"children": {group_id: group}}
    return group_tree, group_graphs


def add_groups(global_graph, groups):
    group_tree, group_graphs = map_group_tree(global_graph, groups)
    for group_id, group in group_tree.items():
        queue = []
        inner_groups = reverse_tree(group, [])
        for inner_group in inner_groups:
            index = next(
                (
                    i
                    for i, item in enumerate(queue)
                    if item["id"] == inner_group["parent"]
                ),
                None,
            )
            if index is None:
                queue.append(
                    {"id": inner_group["parent"], "groups": [inner_group["id"]]}
                )
            else:
                queue[index]["groups"].append(inner_group["id"])

        for item in queue:
            for q_group in item["groups"]:
                group_graphs[item["id"]].subgraph(group_graphs[q_group])

        global_graph.subgraph(group_graphs[group_id])
