import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import click
import xml.etree.ElementTree as ET

# Platform configurations
SUPPORTED_PLATFORMS = ['qiskit', 'pennylane', 'pytket']
PACKAGE_PATHS = {
    'qiskit': [
        '/home/regularuser/qiskit/qiskit/',
        '/home/regularuser/.venv/lib/python3.12/site-packages/qiskit/',
    ],
    'pennylane': [
        '/home/regularuser/.venv/lib/python3.12/site-packages/pennylane/',
    ],
    'pytket': [
        '/home/regularuser/.venv/lib/python3.12/site-packages/pytket/',
    ],
}

# Type aliases for better readability
CoverageData = Dict[str, Dict[str, Any]]
XMLElement = ET.Element


def find_coverage_files(folder_path: str) -> List[Path]:
    """Find XML coverage files in the given folder (non-recursive).

    Args:
        folder_path: Directory path to search for XML files

    Returns:
        List of paths to XML coverage files, excluding merged_coverage.xml
    """
    folder = Path(folder_path)
    return [
        xml_file for xml_file in folder.glob("*.xml")
        if xml_file.name != "merged_coverage.xml"
    ]


def merge_xml_packages(
    merged_root: XMLElement,
    new_root: XMLElement,
) -> None:
    """Merge package elements from new XML into merged XML.

    Args:
        merged_root: Root element of merged XML
        new_root: Root element of new XML to merge
    """
    merged_packages = merged_root.find("packages")
    new_packages = new_root.find("packages")

    if merged_packages is not None and new_packages is not None:
        for package in new_packages.findall("package"):
            merged_packages.append(package)


def merge_coverage_files(xml_files: List[Path]) -> str:
    """Merge multiple XML coverage files into one.

    Args:
        xml_files: List of paths to XML coverage files

    Returns:
        Merged XML content as string
    """
    merged_root = None
    for xml_file in xml_files:
        size_mb = xml_file.stat().st_size / (1024 * 1024)  # Convert bytes to MB
        print(f"Reading {xml_file.name} ({size_mb:.2f} MB)")

        tree = ET.parse(xml_file)
        current_root = tree.getroot()

        if merged_root is None:
            merged_root = current_root
            continue

        merge_xml_packages(
            merged_root=merged_root,
            new_root=current_root,
        )

    return ET.tostring(merged_root, encoding='unicode')


def clean_file_path(file_path: str) -> str:
    """Remove redundant package prefixes from file path.

    Args:
        file_path: Original file path

    Returns:
        Cleaned file path without redundant prefixes
    """
    for platform_paths in PACKAGE_PATHS.values():
        for prefix in platform_paths:
            if file_path.startswith(prefix):
                return file_path[len(prefix):]
    return file_path


def determine_platform(
    file_path: str,
    package_name: str,
) -> Optional[str]:
    """Determine the platform based on file path and package info.

    Args:
        file_path: Path of the source file
        package_name: Name of the package containing the file

    Returns:
        Platform identifier or None if not determined
    """
    if "crates" in package_name:
        return "qiskit"
    if file_path.endswith(".cpp"):
        return "pytket"

    for platform in SUPPORTED_PLATFORMS:
        if f"/site-packages/{platform}/" in file_path:
            return platform

    return "qiskit"  # Default platform


def process_coverage_line(
    line_element: XMLElement,
    file_path: str,
    platform_coverage: CoverageData,
    platform_key: str,
) -> None:
    """Process individual line coverage data.

    Args:
        line_element: XML element containing line coverage info
        file_path: Path of the source file
        platform_coverage: Dictionary to store coverage data
        platform_key: Platform identifier
    """
    line_number = line_element.get('number')
    hit_count = int(line_element.get('hits'))
    line_id = f"{clean_file_path(file_path)}:{line_number}"

    platform_coverage[platform_key]['total_lines'].add(line_id)
    if hit_count > 0:
        platform_coverage[platform_key]['covered_lines'].add(line_id)


def initialize_coverage_data() -> CoverageData:
    """Initialize coverage data structure for all platforms.

    Returns:
        Empty coverage data structure
    """
    return {
        platform: {
            'covered_lines': set(),
            'total_lines': set(),
        }
        for platform in SUPPORTED_PLATFORMS
    }


def process_class_coverage(
    class_element: XMLElement,
    platform_coverage: CoverageData,
    package_name: str,
) -> None:
    """Process coverage data for a class element.

    Args:
        class_element: XML element containing class coverage info
        platform_coverage: Dictionary to store coverage data
        package_name: Name of the package containing the class
    """
    file_path = class_element.get('filename')
    if "test" in file_path.lower() or file_path.endswith(".hpp"):
        return

    platform_key = determine_platform(
        file_path=file_path,
        package_name=package_name,
    )
    if not platform_key:
        return

    lines = class_element.find('lines')
    for line_element in lines.findall('line'):
        process_coverage_line(
            line_element=line_element,
            file_path=file_path,
            platform_coverage=platform_coverage,
            platform_key=platform_key,
        )


def extract_coverage_data(
    root: XMLElement,
) -> CoverageData:
    """Extract coverage data from XML root element.

    Args:
        root: Root element of coverage XML

    Returns:
        Dictionary containing coverage details for each platform
    """
    platform_coverage = initialize_coverage_data()
    packages = root.find('packages')

    for package in packages.findall('package'):
        package_name = package.get('name')
        classes = package.find('classes')
        for class_element in classes.findall('class'):
            process_class_coverage(
                class_element=class_element,
                platform_coverage=platform_coverage,
                package_name=package_name,
            )

    return platform_coverage


def calculate_coverage_metrics(
    platform_coverage: CoverageData,
) -> CoverageData:
    """Calculate coverage metrics for each platform.

    Args:
        platform_coverage: Raw coverage data

    Returns:
        Coverage data with calculated metrics
    """
    for platform, coverage_data in platform_coverage.items():
        total_lines = len(coverage_data['total_lines'])
        covered_lines = len(coverage_data['covered_lines'])
        coverage_percentage = (
            covered_lines / total_lines * 100 if total_lines > 0 else 0
        )

        platform_coverage[platform].update({
            'coverage_percentage': coverage_percentage,
            'total': total_lines,
            'covered': covered_lines,
        })

        print(
            f"{platform}: {coverage_percentage:.2f}% line coverage ({covered_lines}/{total_lines})")

    return platform_coverage


def analyze_coverage(coverage_path: str) -> CoverageData:
    """Analyze coverage data from XML report.

    Args:
        coverage_path: Path to coverage XML file

    Returns:
        Processed coverage data for all platforms
    """
    root = ET.parse(coverage_path).getroot()
    coverage_data = extract_coverage_data(root=root)
    return calculate_coverage_metrics(platform_coverage=coverage_data)


def save_coverage_results(
    coverage_data: CoverageData,
    output_path: Path,
) -> None:
    """Save coverage results to JSON file.

    Args:
        coverage_data: Coverage data to save
        output_path: Path to save JSON file
    """
    serializable_data = {
        platform: {
            **data,
            'total_lines': list(data['total_lines']),
            'covered_lines': list(data['covered_lines']),
        }
        for platform, data in coverage_data.items()
    }
    with open(output_path, "w") as f:
        json.dump(serializable_data, f, indent=2)


def process_coverage(folder_path: str) -> None:
    """Process coverage files and generate reports."""
    folder = Path(folder_path)
    merged_xml_path = folder / "merged_coverage_cli.xml"
    json_path = folder / "coverage_platforms.json"

    # if merged_xml_path.exists():
    #     print("Process skipped: merged_coverage.xml already exists.")
    #     return

    xml_files = find_coverage_files(folder_path=str(folder))
    # exclude "merged_coverage*.xml" files
    xml_files = [
        xml_file for xml_file in xml_files
        if not xml_file.name.startswith("merged_coverage")]
    if not xml_files:
        print("No XML files found in the specified folder.")
        return

    try:
        merged_xml = merge_coverage_files(xml_files=xml_files)
        with open(merged_xml_path, "w") as f:
            f.write(merged_xml)

        coverage_data = analyze_coverage(coverage_path=str(merged_xml_path))
        save_coverage_results(
            coverage_data=coverage_data,
            output_path=json_path,
        )

        print(f"Coverage analysis complete. Output files created:")
        print(f"  - {merged_xml_path}")
        print(f"  - {json_path}")

    except Exception as e:
        raise click.ClickException(f"Error during processing: {e}")


@click.command()
@click.option(
    '--folder_path',
    required=True,
    type=click.Path(exists=True),
    help='Path to folder containing coverage files, or path to a .txt file containing the folder path',
)
def main(folder_path: str) -> None:
    """Process coverage files and generate merged reports.

    The folder_path can be either:
    - A direct path to a folder containing coverage files
    - A path to a .txt file, in which case the first line of the file is used as the folder path

    Example usage:
        $ python -m qite.compute_coverage --folder_path /path/to/coverage/files
        $ python -m qite.compute_coverage --folder_path /path/to/folder_path.txt
    """
    if folder_path.endswith('.txt'):
        with open(folder_path, 'r') as f:
            folder_path = f.readline().strip()

    process_coverage(folder_path)


if __name__ == "__main__":
    main()
