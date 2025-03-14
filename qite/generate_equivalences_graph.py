import matplotlib.pyplot as plt
import click
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from rich.console import Console
import json
import subprocess
from mqt import qcec


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
