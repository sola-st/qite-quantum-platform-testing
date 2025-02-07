import matplotlib.pyplot as plt
import click
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from rich.console import Console
import json
import subprocess
from mqt import qcec

"""
To create a well-specified task description, we need to clarify several aspects of the task. Here are some questions to cover potential blind spots:

1. **Input/Output Specifications:**
   - What is the exact format of the QASM files and metadata files?
   - How should the function handle errors (e.g., missing files, invalid QASM content)?
   - Should the function return any other outputs besides the graph PNG file?

2. **QCEC Tool:**
   - How is the QCEC tool invoked (e.g., command-line tool, Python library)?
   - What are the expected inputs and outputs of the QCEC tool?

3. **Graph Details:**
   - Should the graph include any additional information (e.g., node labels, edge weights)?
   - Are there any specific requirements for the graph's appearance (e.g., layout, font size)?

4. **Metadata Handling:**
   - How should the function handle cases where metadata is missing or incomplete?
   - Are there any additional metadata fields that need to be processed?

5. **Implementation Details:**
   - Are there any specific libraries or tools that should be used for graph generation?
   - Should the function be implemented as a standalone script or as part of a larger project?

Based on these questions, here is a refined task description:

---

### Task Description

**Objective:**
Implement a command-line interface (CLI) in Python that processes a list of QASM files and their associated metadata to generate a graph representing the equivalence results between pairs of QASM files.

**Inputs:**
1. A folder containing QASM files and their corresponding metadata files (JSON format). Each QASM file has a corresponding metadata file with the same name but a different extension.
2. The metadata JSON files contain a field `platform` which can have values `qiskit`, `pytket`, or `pennylane`.

**Outputs:**
1. A PNG file named `graph_equivalences.png` in the same folder, representing the equivalence results between QASM files.

**Functionality:**
1. **File Processing:**
   - Read all QASM files and their corresponding metadata files from the specified folder.
   - Ensure that each QASM file has a corresponding metadata file.

2. **Equivalence Checking:**
   - Compute all pairs of QASM files.
   - For each pair, run the QCEC tool to determine their equivalence.
   - Collect the results as triplets `(qasmA, qasmB, equivalence_result)`.

3. **Graph Generation:**
   - Create a graph where each QASM file is a node.
   - Add undirected edges between nodes representing the comparison results.
   - Label each edge with the equivalence result string.
   - Color edges red if the equivalence result is `not_equivalent`.
   - Color nodes based on the `platform` field in the metadata:
     - `qiskit`: purple
     - `pytket`: gray
     - `pennylane`: magenta

4. **Output:**
   - Save the generated graph as `graph_equivalences.png` in the specified folder.

**Requirements:**
- Use the NetworkX library for graph generation.
- Handle errors gracefully (e.g., missing files, invalid content).
- Ensure the function is well-documented and includes usage instructions.

**Example Usage:**
```bash
python -m qite.generate_equivalences_graph  --input_folder /tmp/tmps6tkuhco
```


# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate
- make sure that any output folder exists before storing file in it, otherwise create it.

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports
Make sure to add a function and call that function only in the main cli command.
The goal is to be able to import that function also from other files.


"""

console = Console()


def read_metadata(file_path: Path) -> Dict[str, Any]:
    with file_path.open('r') as file:
        return json.load(file)


def run_qcec(qasm_a: Path, qasm_b: Path) -> str:
    try:
        result = qcec.verify(
            str(qasm_a),
            str(qasm_b),
            transform_dynamic_circuit=True)
        return str(result.equivalence)
    except Exception as e:
        return f"error: {e}"


def create_graph(
        equivalences: List[Tuple[str, str, str]],
        metadata: Dict[str, Dict[str, str]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for qasm_a, qasm_b, result in equivalences:
        default_metadata = {'platform': 'generator'}

        graph.add_node(qasm_a, platform=metadata.get(
            qasm_a, default_metadata)['platform'])
        graph.add_node(qasm_b, platform=metadata.get(
            qasm_b, default_metadata)['platform'])
        graph.add_edge(qasm_a, qasm_b, label=result, color='red'
                       if result == 'not_equivalent' else 'black',
                       connectionstyle='arc3, rad = 0.1')
        graph.add_edge(qasm_b, qasm_a, label=result, color='red'
                       if result == 'not_equivalent' else 'black',
                       connectionstyle='arc3, rad = 0.1')

    for meta in metadata.values():
        input_qasm = Path(meta.get('input_qasm', '')).stem
        output_qasm = Path(meta.get('output_qasm', '')).stem
        if input_qasm and output_qasm:
            graph.add_edge(input_qasm, output_qasm, color='blue', width=2.0)

    return graph


def save_graph(graph: nx.MultiDiGraph, output_path: Path) -> None:
    pos = nx.spring_layout(graph)
    edge_labels = {(u, v, k): d.get('label', '')
                   for u, v, k, d in graph.edges(data=True, keys=True)}
    edge_colors = [d.get('color', 'black')
                   for u, v, k, d in graph.edges(data=True, keys=True)]
    node_colors = [
        get_node_color(graph.nodes[node].get('platform', ''))
        for node in graph.nodes()]

    console.print(f"NetworkX version: {nx.__version__}")

    plt.figure(figsize=(12, 12))
    nx.draw(graph, pos, edge_color=edge_colors, node_color=node_colors,
            with_labels=True, connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=edge_labels)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def get_node_color(platform: str) -> str:
    return {'qiskit': 'lime', 'pytket': 'gray', 'pennylane': 'magenta'}.get(platform, 'white')


@click.command()
@click.option('--input_folder', required=True, type=click.Path(
    exists=True, file_okay=False, path_type=Path))
@click.option('--prefix', required=False, type=int)
def main(input_folder: Path, prefix: Optional[int]) -> None:
    generate_equivalence_graph(input_folder, prefix)


def generate_equivalence_graph(
        input_folder: Path, prefix: Optional[int]) -> None:
    prefix_str = str(prefix).zfill(7) if prefix is not None else ''
    qasm_files = [file for file in input_folder.glob(
        '*.qasm') if file.stem.startswith(prefix_str)]
    all_metadata = [
        read_metadata(file) for file in input_folder.glob('*.json')]
    metadata_files = {
        Path(metadata["output_qasm"]).stem: metadata
        for metadata in all_metadata}

    equivalences = []
    for i, qasm_a in enumerate(qasm_files):
        for qasm_b in qasm_files[i+1:]:
            result = run_qcec(qasm_a, qasm_b)
            equivalences.append((qasm_a.stem, qasm_b.stem, result))

    graph = create_graph(equivalences, metadata_files)
    output_filename = f"{prefix_str}_equivalence_graph.png" if prefix_str else "equivalence_graph.png"
    print(f"Saving graph to: {input_folder / output_filename}")
    save_graph(graph, input_folder / output_filename)


if __name__ == '__main__':
    main()
