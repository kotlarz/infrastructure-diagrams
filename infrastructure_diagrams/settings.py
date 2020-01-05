DEFAULT_GRAPH_ENGINE = "neato"

DEFAULT_CUSTOM_VARIABLES = {
    "colors": {
        "background": "#1BA1E2",
        "border": "#008A00",
        "title": "#008A00",
        "subtitle": "#008A00",
        "edge_text": "#008A00",
    }
}

DEFAULT_GLOBAL_GRAPH_ATTRIBUTES = {
    "label": "",
    "splines": "ortho",
    "fontname": "monospace",
}

DEFAULT_GROUP_ATTRIBUTES = {
    "fontname": "monospace",
}

DEFAULT_NODE_ATTRIBUTES = {
    "shape": "box",
    "fillcolor": "white",
    "style": "filled",
    "fontname": "monospace",
}

DEFAULT_EDGE_ATTRIBUTES = {
    "fontname": "monospace",
}

IGNORE_GRAPH_ATTRIBUTES = []
IGNORE_GROUP_ATTRIBUTES = ["id", "nodes", "parent_group"]
IGNORE_NODE_ATTRIBUTES = ["id", "edges"]
IGNORE_EDGE_ATTRIBUTES = ["node"]

COPYRIGHT_STRING = "drawn by infrastructure-diagrams"
