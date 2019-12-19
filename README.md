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

Example output of `example.yaml` from the [examples/](https://github.com/kotlarz/infrastructure-diagrams/examples/example.yaml) directory:

Output:
![Output of example.yaml](https://raw.githubusercontent.com/kotlarz/infrastructure-diagrams/master/examples/example.png)

Example diagram configuration files can be found under the [examples/](https://github.com/kotlarz/infrastructure-diagrams/) directory.
