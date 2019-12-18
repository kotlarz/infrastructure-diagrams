# infrastructure-diagrams

infrastructure-diagrams is a python package that allows creating infrastructure diagrams/graphs from configuration files (YAML and JSON). The package utilizes [Graphviz](https://www.graphviz.org/) to generate the diagrams. The functionality is exposed in the command line by the Unix command file.

## Requirements

The package requires `python >= 3.6`.
It has only been tested on Linux as the intended use was for automatically generating diagrams in a CI.

## Installation

The current stable version of infrastructure-daigrams is available on pypi and can be installed by running `pip install infrastructure-diagrams`.

Other sources:

- pypi: http://pypi.python.org/pypi/infrastructure-diagrams/
- github: https://github.com/kotlarz/infrastructure-diagrams/

## Usage

```bash
$ infrastructure-diagrams
usage: infrastructure-diagrams [-h] [-d DISPLAY] [-o OUTPUT] [-r RENDERER] file

positional arguments:
  file                  path to diagram file

optional arguments:
  -h, --help            show this help message and exit
  -d DISPLAY, --display DISPLAY
                        display the diagram after rendering
  -o OUTPUT, --output OUTPUT
                        output path for the diagram, including filetype (.svg, .png, etc.)
  -r RENDERER, --renderer RENDERER
                        output renderer used for rendering (cairo, gd, etc.)
```

Example:
`$ infrastructure-diagrams -o example.png examples/example.yaml`

## Configuration files

The configuration files extend the Graphviz [Node, Edge and Graph Attributes](https://www.graphviz.org/doc/info/attrs.html), meaning you can customize the diagram / graph as needed.

Example, `misc.yaml` from the [examples/](https://github.com/kotlarz/infrastructure-diagrams/examples/misc.yaml) directory:

```yaml
graph_attributes:
  # https://www.graphviz.org/doc/info/attrs.html#d:fontsize
  fontsize: 20
  label: Simple Diagram
graph_engine: dot
groups:
  - id: group1
    label: "Group (ID: 1)"
    # https://www.graphviz.org/doc/info/attrs.html#d:style
    style: filled
    # https://www.graphviz.org/doc/info/attrs.html#d:fillcolor
    fillcolor: "#cccccc"
    nodes:
      # Group 1 node 1
      - id: g1_node1
        label: Node G1_1
        edges:
          - node: G2_1
            label: Edge between node G1_1 and G2_1
            # https://www.graphviz.org/doc/info/attrs.html#d:color
            color: brown
            fontcolor: brown
          - node: global_node_1
            label: Edge between node G1_1 and global_node_1
  - id: group2
    parent_group: group1
    label: "Group (ID: 2)"
    style: filled
    fillcolor: "#aaaaaa"
    color: purple
    nodes:
      # Group 2 node 1
      - id: G2_1
        label: Node G2_1
        style: filled
        fillcolor: "#0026ca:#7a7cff"
        fontcolor: white
      - id: G2_2
        label: Node G2_2
        # https://www.graphviz.org/doc/info/shapes.html
        shape: box
        color: green
        edges:
          - node: G2_1
      - id: G2_3
        label: Node G2_3
        edges:
          - node: global_node_2
            label: Edge between node G2_3 and global_node_2
            color: red
global_nodes:
  - id: global_node_1
    label: Global Node 1
    edges:
      - node: global_node_2
        label: Edge between Global node 1 and 2
  - id: global_node_2
    label: Global Node 2
    shape: star
```

Output:
![Output of misc.yaml](https://raw.githubusercontent.com/kotlarz/infrastructure-diagrams/master/examples/misc.png)

Example diagram configuration files can be found under the [examples/](https://github.com/kotlarz/infrastructure-diagrams/) directory.
