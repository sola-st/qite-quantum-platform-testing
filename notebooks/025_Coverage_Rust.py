#!/usr/bin/env python
# coding: utf-8

# In[3]:

# Standard library imports
from functools import lru_cache
import subprocess
from matplotlib_venn import venn2
import random
import xml.etree.ElementTree as ET
import os
import re
import sys
import json
from typing import List, Tuple, Dict, Any, Optional, Set
from multiprocessing import Pool
from pathlib import Path

# Third-party data processing and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Progress bar utilities
from tqdm.auto import tqdm
from pandarallel import pandarallel
from dataclasses import dataclass
from typing import Set, Tuple, Optional
from matplotlib_venn import venn2
import seaborn as sns

# Initialize parallel processing
tqdm.pandas()
pandarallel.initialize(progress_bar=True)

# In[49]:

PLATFORMS = [
    'qiskit', 'pennylane', 'pytket',
    # 'bqskit'
]

EXPERIMENTS_QITE = {
    "2025_02_28__00_40": {
        "path": "../program_bank/v043/2025_02_28__00_40",
        "description": "QITE: 1 h - 3 platforms - Rust and Cpp"
    },
    "2025_03_05__02_33": {
        "path": "../program_bank/v045/2025_03_05__02_33",
        "description": "QITE: 8h - 2 generators"
    },
    # "2025_03_05__17_47": {
    #     "path": "../program_bank/v046/2025_03_05__17_47",
    #     "description": "Option A: 1h - 3 platforms"
    # },
    # "2025_03_05__21_56": {
    #     "path": "../program_bank/v046/2025_03_05__21_56",
    #     "description": "1h - 3 platforms"
    # },
    # "2025_03_06__00_18": {
    #     "path": "../program_bank/v046/2025_03_06__00_18",
    #     "description": "1h - 3 platforms"
    # },
    # "2025_03_05__23_24": {
    #     "path": "../program_bank/v046/2025_03_05__23_24",
    #     "description": "1h - 3 platforms"
    # },
    # "2025_03_06__10_47": {
    #     "path": "../program_bank/v046/2025_03_06__10_47",
    #     "description": "1h - 3 platforms"
    # },
    # "2025_03_06__12_58": {
    #     "path": "../program_bank/v046/2025_03_06__12_58",
    #     "description": "1h - 3 platforms"
    # },
    # "2025_03_06__23_35": {
    #     "path": "../program_bank/v046/2025_03_06__23_35",
    #     "description": "1h - 3 platforms - new timeout"
    # },
    # "2025_03_07__01_30": {
    #     "path": "../program_bank/v046/2025_03_07__01_30",
    #     "description": "1h - 3 platforms  - new timeout"
    # },
    # "2025_03_07__01_31": {
    #     "path": "../program_bank/v046/2025_03_07__01_31",
    #     "description": "1h - 3 platforms  - new timeout"
    # },
    # "2025_03_07__01_32": {
    #     "path": "../program_bank/v046/2025_03_07__01_32",
    #     "description": "1h - 3 platforms  - new timeout"
    # },
    # "2025_03_07__01_33": {
    #     "path": "../program_bank/v046/2025_03_07__01_31",
    #     "description": "8h - 3 platforms  - new timeout"
    # },
    # "2025_03_07__01_35": {
    #     "path": "../program_bank/v046/2025_03_07__01_31",
    #     "description": "8h - 3 platforms  - new timeout"
    # },
    "2025_03_07__15_21": {
        "path": "../program_bank/v046_debug/2025_03_07__15_21",
        "description": "1h - 3 platforms  - new timeout"
    },
    "2025_03_07__16_14": {
        "path": "../program_bank/v046_debug/2025_03_07__16_14",
        "description": "1h - 3 platforms  - new timeout"
    },
    # program_bank/v046_debug/2025_03_07__16_29
    "2025_03_07__16_29": {
        "path": "../program_bank/v046_debug/2025_03_07__16_29",
        "description": "1h - 3 platforms  - threads "
    },
}

SELECTED_EXP_QITE = "2025_03_07__16_29"
SELECTED_EXP_QITE_MULTIPLE = [
    SELECTED_EXP_QITE,
]

EXPERIMENTS_MORPHQ = {
    "v14": {
        "path": "/home/paltenmo/projects/morphq_upgraded/MorphQ-Quantum-Qiskit-Testing-ICSE-23/data/qmt_v14",
        "description": "MorphQ Data - 1h - Qiskit"
    }
}
SELECTED_EXP_MORPHQ = "v14"


# In[50]:


def merge_cobertura_reports(report1_path, report2_path, output_path):
    tree1 = ET.parse(report1_path)
    root1 = tree1.getroot()

    tree2 = ET.parse(report2_path)
    root2 = tree2.getroot()

    # Merge `<packages>` elements
    packages1 = root1.find("packages")
    packages2 = root2.find("packages")

    if packages1 is not None and packages2 is not None:
        for package in packages2.findall("package"):
            packages1.append(package)

    # Save merged XML
    tree1.write(output_path)


def prepare_xml_morphq(base_path: str):
    """
    Prepare XML coverage files for MorphQ by merging multiple coverage files into one.

    Args:
        base_path (str): Base path containing the coverage files
    """

    # Get paths for different coverage files
    py_coverage = os.path.join(base_path, "coverage.xml")
    rust_coverage = os.path.join(base_path, "rust_coverage.xml")
    merged_coverage = os.path.join(base_path, "merged_coverage.xml")

    if os.path.exists(merged_coverage):
        print(f"Coverage file already exists: {merged_coverage}")
        return
    # Merge Python and Rust coverage
    merge_cobertura_reports(
        report1_path=py_coverage,
        report2_path=rust_coverage,
        output_path=merged_coverage
    )


def prepare_xml_ours(base_path: str):
    """
    Prepare XML coverage files by merging multiple coverage files into one.

    Args:
        base_path (str): Base path containing the coverage files
    """
    # Get paths for different coverage files
    py_coverage = os.path.join(base_path, "coverage.xml")
    rust_coverage = os.path.join(base_path, "rust_coverage.xml")
    cpp_coverage = os.path.join(base_path, "cpp_coverage.xml")
    converter_coverage = os.path.join(base_path, "converter_coverage.xml")
    merged_coverage = os.path.join(base_path, "merged_coverage.xml")
    if os.path.exists(merged_coverage):
        print(f"Coverage file already exists: {merged_coverage}")
        return

    # Merge Python and Rust coverage
    merge_cobertura_reports(
        report1_path=py_coverage,
        report2_path=rust_coverage,
        output_path=merged_coverage
    )

    # Add C++ coverage
    merge_cobertura_reports(
        report1_path=cpp_coverage,
        report2_path=merged_coverage,
        output_path=merged_coverage
    )

    # Add converter coverage if exists
    if os.path.exists(converter_coverage):
        merge_cobertura_reports(
            report1_path=merged_coverage,
            report2_path=converter_coverage,
            output_path=merged_coverage
        )


# In[52]:

for experiment_name, experiment_data in EXPERIMENTS_QITE.items():
    prepare_xml_ours(base_path=experiment_data["path"])

for experiment_name, experiment_data in EXPERIMENTS_MORPHQ.items():
    prepare_xml_morphq(base_path=experiment_data["path"])


# In[ ]:

# Constants for commonly used prefixes in file paths
QISKIT_PREFIX = "/home/regularuser/qiskit/qiskit/"
QISKIT_SITE_PACKAGES_PREFIX = "/home/regularuser/.venv/lib/python3.12/site-packages/qiskit/"
PYTKET_SITE_PACKAGES_PREFIX = "/home/regularuser/.venv/lib/python3.12/site-packages/pytket/"
PENNYLANE_SITE_PACKAGES_PREFIX = "/home/regularuser/.venv/lib/python3.12/site-packages/pennylane/"


def _remove_redundant_prefix(line_identifier: str) -> str:
    """
    Removes redundant prefixes from a line identifier.

    Args:
        line_identifier (str): The line identifier to clean.

    Returns:
        str: The cleaned line identifier.
    """
    for prefix in [
        QISKIT_PREFIX,
        QISKIT_SITE_PACKAGES_PREFIX,
        PYTKET_SITE_PACKAGES_PREFIX,
        PENNYLANE_SITE_PACKAGES_PREFIX
    ]:
        if line_identifier.startswith(prefix):
            line_identifier = line_identifier[len(prefix):]
    return line_identifier


def _extract_platform_from_filename(
        filename: str, platforms: List[str]) -> str:
    """
    Determines the platform based on the file path.

    Args:
        filename (str): The name of the file.
        platforms (List[str]): List of platform names.

    Returns:
        str: The identified platform key, or None if not found.
    """
    for platform_name in platforms:
        if f"/site-packages/{platform_name}/" in filename:
            return platform_name
    return None


def parse_cobertura_xml(coverage_path: str) -> ET.Element:
    """
    Parses a Cobertura XML report.

    Args:
        coverage_path (str): Path to the Cobertura XML coverage report.

    Returns:
        ET.Element: The root element of the parsed XML tree.
    """
    tree = ET.parse(coverage_path)
    return tree.getroot()


def extract_coverage_data(
    root: ET.Element, platforms: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Extracts coverage data for specified platforms from a Cobertura XML root element.

    Args:
        root (ET.Element): The root element of the Cobertura XML report.
        platforms (List[str]): List of platform names to extract coverage information for.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary containing coverage details for each platform.
    """
    platform_coverage = {
        platform: {
            'covered_lines': set(),
            'total_lines': set(),
        } for platform in platforms
    }

    packages = root.find('packages')
    for package in packages.findall('package'):
        classes = package.find('classes')
        for class_element in classes.findall('class'):
            filename = class_element.get('filename')

            if "test" in filename.lower() or filename.endswith(".hpp"):
                continue

            lines = class_element.find('lines')
            for line_element in lines.findall('line'):
                line_number = line_element.get('number')
                hits = int(line_element.get('hits'))
                line_identifier = f"{filename}:{line_number}"

                platform_key = _extract_platform_from_filename(
                    filename, platforms)

                if "crates" in package.get('name'):
                    platform_key = "qiskit"
                elif filename.endswith(".cpp"):
                    platform_key = "pytket"
                else:
                    if not platform_key:
                        platform_key = "qiskit"

                if platform_key:
                    line_identifier = _remove_redundant_prefix(
                        line_identifier)
                    platform_coverage[platform_key]['total_lines'].add(
                        line_identifier)
                    if hits > 0:
                        platform_coverage[platform_key]['covered_lines'].add(
                            line_identifier)

    return platform_coverage


def calculate_coverage_percentage(
    platform_coverage:
    Dict[str, Dict[str, Any]]) -> Dict[str,
                                       Dict[str, Any]]:
    """
    Calculates coverage percentages for each platform.

    Args:
        platform_coverage (Dict[str, Dict[str, Any]]): Dictionary containing raw coverage data.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with added coverage percentage for each platform.
    """
    for platform, coverage_data in platform_coverage.items():
        total_lines = len(coverage_data['total_lines'])
        covered_lines = len(coverage_data['covered_lines'])
        coverage_percentage = (
            covered_lines / total_lines) * 100 if total_lines > 0 else 0

        platform_coverage[platform]['coverage_percentage'] = coverage_percentage
        platform_coverage[platform]['total_lines'] = set(list(
            coverage_data['total_lines']))
        platform_coverage[platform]['covered_lines'] = set(list(
            coverage_data['covered_lines']))
        platform_coverage[platform]['total'] = total_lines
        platform_coverage[platform]['covered'] = covered_lines

    return platform_coverage


def get_coverage_info(coverage_path: str, platforms: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves coverage information for specified platforms from a Cobertura XML report.

    Args:
        coverage_path (str): Path to the Cobertura XML coverage report.
        platforms (List[str]): List of platform names to extract coverage information for.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary containing coverage details for each platform.
    """
    root = parse_cobertura_xml(coverage_path)
    platform_coverage = extract_coverage_data(root, platforms)
    platform_coverage = calculate_coverage_percentage(platform_coverage)

    return platform_coverage


def print_coverage_summary(package_coverage: Dict[str, Dict[str, Any]]):
    """Prints a formatted summary of coverage information."""
    for package, coverage in package_coverage.items():
        print(
            f"{package:_<15}: {coverage['coverage_percentage']:.2f}% ({coverage['covered']}/{coverage['total']})")

# In[45]:


# Get coverage information for each experiment in EXPERIMENTS_QITE
package_coverage_ours = {}

for experiment_name, experiment_data in EXPERIMENTS_QITE.items():
    coverage_path = os.path.join(
        experiment_data["path"],
        "merged_coverage.xml")
    package_coverage = get_coverage_info(
        coverage_path, PLATFORMS)
    package_coverage_ours[experiment_name] = package_coverage

    print(f"Coverage Summary for QITE Experiment: {experiment_name}")
    print_coverage_summary(package_coverage)

# Get coverage information for each experiment in EXPERIMENTS_MORPHQ
package_coverage_morphq = {}

for experiment_name, experiment_data in EXPERIMENTS_MORPHQ.items():
    coverage_path = os.path.join(
        experiment_data["path"],
        "merged_coverage.xml")
    package_coverage = get_coverage_info(
        coverage_path, PLATFORMS)
    package_coverage_morphq[experiment_name] = package_coverage

    print(f"Coverage Summary for MorphQ Experiment: {experiment_name}")
    print_coverage_summary(package_coverage)


# In[45]:
# Set the seed for reproducibility
random.seed(42)

# Extract total lines for 'qiskit' from both experiments
qiskit_total_lines = set(
    package_coverage_ours[SELECTED_EXP_QITE]["qiskit"]
    ["total_lines"])
qiskit_total_lines_morphq = set(
    package_coverage_morphq[SELECTED_EXP_MORPHQ]
    ["qiskit"]["total_lines"])

# Assert that both sets have the same lines
try:
    assert qiskit_total_lines == qiskit_total_lines_morphq, \
        "QITE and MorphQ have different sets of total lines"
    print("✓ QITE and MorphQ have identical sets of total lines")
    print(f"Total number of lines: {len(qiskit_total_lines)}")
except AssertionError as e:
    print("✗ Error:", e)
    # Print diagnostic information
    only_in_qite = qiskit_total_lines - qiskit_total_lines_morphq
    only_in_morphq = qiskit_total_lines_morphq - qiskit_total_lines
    print(f"Lines only in QITE: {len(only_in_qite)}")
    print(f"Lines only in MorphQ: {len(only_in_morphq)}")
    # Show some example differences
    if only_in_qite:
        print("\nExample lines only in QITE:")
        for line in sorted(only_in_qite)[:5]:
            print(f"  {line}")
    if only_in_morphq:
        print("\nExample lines only in MorphQ:")
        for line in sorted(only_in_morphq)[:5]:
            print(f"  {line}")


# In[8]:


# Define global constants for colors
PLATFORM_COLORS = {
    'qiskit': 'mediumslateblue',
    'pytket': 'silver',
    'pennylane': 'orchid'
}
OUTPUT_DIR = "images"
OUTPUT_PATH_BAR_PLOT = os.path.join(
    OUTPUT_DIR, "platform_coverage_bar_plot.pdf")


def create_platform_bar_plot(package_coverage, platforms, output_path):
    """
    Generates and saves a horizontal bar plot of platform coverage.

    Args:
        package_coverage (Dict[str, Dict[str, Any]]): Coverage data for each platform.
        platforms (List[str]): List of platforms to include in the plot.
        output_path (str): Path to save the generated plot.
    """
    platform_colors = [PLATFORM_COLORS[platform] for platform in platforms]
    total_lines_covered = [package_coverage[platform]['covered']
                           for platform in platforms]

    fig, ax = plt.subplots(figsize=(5, 2))
    bars = ax.barh(platforms, total_lines_covered, color=platform_colors)
    ax.set_xlabel('Total Lines Covered')
    ax.set_ylabel('Platform')

    max_val = max(total_lines_covered)
    add_bar_value_labels(ax, bars, total_lines_covered, max_val)

    ax.set_xlim(0, max_val * 1.2)
    fig.tight_layout()

    plt.show()
    fig.savefig(output_path)


def add_bar_value_labels(ax, bars, values, max_val):
    """
    Adds labels to the end of each bar in a horizontal bar plot.

    Args:
        ax (matplotlib.axes.Axes): The axes object containing the bar plot.
        bars (matplotlib.container.BarContainer): The bar container object.
        values (List[float]): List of values corresponding to each bar.
        max_val (float): Maximum value among the data, used for scaling label position.
    """
    for bar, value in zip(bars, values):
        ax.text(value + (max_val / 30), bar.get_y() + bar.get_height() / 2,
                f'{value}', va='center', ha='left')


def print_latex_commands(package_coverage, platforms):
    """
    Prints LaTeX commands for total and covered lines for each platform.

    Args:
        package_coverage (Dict[str, Dict[str, Any]]): Coverage data for each platform.
        platforms (List[str]): List of platforms to generate commands for.
    """
    for platform in platforms:
        total_lines = package_coverage[platform]['total']
        covered_lines = package_coverage[platform]['covered']
        print(
            f"\\newcommand{{\\QITE{platform.capitalize()}TotalLines}}{{{total_lines}}}")
        print(
            f"\\newcommand{{\\QITE{platform.capitalize()}CoveredLines}}{{{covered_lines}}}")


# Main execution
create_platform_bar_plot(
    package_coverage=package_coverage_ours[SELECTED_EXP_QITE],
    platforms=PLATFORMS,
    output_path=OUTPUT_PATH_BAR_PLOT,
)
print_latex_commands(
    package_coverage=package_coverage_ours[SELECTED_EXP_QITE],
    platforms=PLATFORMS)

# In[9]:


def sample_and_print_lines(covered_lines, total_lines, num_samples=30):
    """
    Samples and prints covered and uncovered lines.

    Args:
        covered_lines (set): Set of covered lines.
        total_lines (set): Set of total lines.
        num_samples (int): Number of lines to sample from each category.
    """
    # Set the seed for reproducibility
    random.seed(42)

    # Calculate the uncovered lines
    uncovered_lines = set(total_lines) - set(covered_lines)

    # Sample lines from each group
    sampled_covered = random.sample(
        covered_lines, min(num_samples, len(covered_lines)))
    sampled_uncovered = random.sample(
        uncovered_lines, min(num_samples, len(uncovered_lines)))

    # Print the sampled lines
    print("Sampled Covered Lines:")
    for line in sampled_covered:
        print(line)

    print("\nSampled Uncovered Lines:")
    for line in sampled_uncovered:
        print(line)


# pennylane_covered = package_coverage_ours["pennylane"]["covered_lines"]
# pennylane_total = package_coverage_ours["pennylane"]["total_lines"]

# sample_and_print_lines(pennylane_covered, pennylane_total)


# In[10]:

def create_line_coverage_data(
    total_lines: Set[str],
    covered_lines: Set[str],
) -> List[Dict]:
    """
    Creates a list of dictionaries containing coverage information for each line.

    Args:
        total_lines: Set of all code lines
        covered_lines: Set of covered code lines

    Returns:
        List of dictionaries with coverage details for each line
    """
    line_data = []
    covered_lines_set = set(covered_lines)

    for line in total_lines:
        file_path, line_number = line.split(':')
        top_level_folder = file_path.split(
            '/')[0] if '/' in file_path else "root"

        line_data.append({
            'filename': file_path,
            'line_number': int(line_number),
            'covered': line in covered_lines_set,
            'top_level_folder': top_level_folder
        })

    return line_data


def plot_folder_coverage(coverage_df: pd.DataFrame) -> None:
    """
    Creates a stacked bar plot showing covered and uncovered lines by folder.

    Args:
        coverage_df: DataFrame containing coverage information
    """

    # Group data by folder and coverage status, count occurrences
    grouped_coverage = coverage_df.groupby(
        ['top_level_folder', 'covered']
    ).size().unstack(fill_value=0)
    # convert columns headers to strings
    grouped_coverage.columns = grouped_coverage.columns.astype(str)
    # swap columns to have covered first
    grouped_coverage = grouped_coverage[['True', 'False']]
    # Sort folders by number of covered (True) then uncovered (False) lines
    grouped_coverage = grouped_coverage.sort_values(
        by=['True', 'False'],
        ascending=False,)
    # Create a new figure with specified size
    plt.figure(figsize=(12, 6))

    # Create horizontal stacked bar plot
    grouped_coverage.plot(
        kind='barh',         # horizontal bars
        stacked=True,        # stack bars for covered/uncovered
        # green for covered, red for uncovered
        color=['forestgreen', 'firebrick'],
    )

    # Set plot labels and title
    plt.title('Line Coverage by Top Level Folder')
    plt.xlabel('Number of Lines')
    plt.ylabel('Folder')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add legend with custom labels
    plt.legend(title='Coverage Status', labels=['Covered', 'Uncovered'])

    # Adjust layout to prevent label clipping
    plt.tight_layout()

    # Display the plot
    plt.show()


# Extract PennyLane coverage data
# Create plots for all platforms
for platform in PLATFORMS:
    print(f"\nAnalyzing {platform} coverage:")
    platform_coverage = package_coverage_ours[SELECTED_EXP_QITE][platform]
    coverage_data = create_line_coverage_data(
        total_lines=platform_coverage["total_lines"],
        covered_lines=platform_coverage["covered_lines"],
    )

    # Create and display coverage analysis
    coverage_df = pd.DataFrame(coverage_data)
    print(f"\n{platform.capitalize()} Coverage by Folder:")
    plot_folder_coverage(coverage_df=coverage_df)


# In[ ]:

def compare_sets(
        set1, set2, name1="Set 1", name2="Set 2", top_k=10, color1="blue",
        color2="red", print_elements=False):
    """
    Compare two sets and print their differences in a formatted way.

    Args:
    set1: First set to compare
    set2: Second set to compare
    name1: Name identifier for first set
    name2: Name identifier for second set
    top_k: Number of elements to print from each difference (default: 10)
    color1: Color for first set's plot (default: "blue")
    color2: Color for second set's plot (default: "red")
    print_elements: Whether to print individual elements (default: False)

    Returns:
    None
    """
    set1_unique = set(set1)
    set2_unique = set(set2)

    # Difference in sizes
    print(f"Size of {name1}: {len(set1_unique)}")
    print(f"Size of {name2}: {len(set2_unique)}")

    # Elements present in set1 but not in set2
    diff_set1 = set1_unique - set2_unique
    if print_elements:
        print(f"\nElements in {name1} but not in {name2}: {len(diff_set1)}")
        for item in sorted(diff_set1)[:top_k]:
            print(f"  {item}")

    # Elements present in set2 but not in set1
    diff_set2 = set2_unique - set1_unique
    if print_elements:
        print(f"\nElements in {name2} but not in {name1}: {len(diff_set2)}")
        for item in sorted(diff_set2)[:top_k]:
            print(f"  {item}")

    # remove the line number:
    diff_set1_files = [line.split(":")[0] for line in diff_set1]
    diff_set2_files = [line.split(":")[0] for line in diff_set2]

    # print countplot of the differences make it horizontal and keep only the
    # top 10 most popular files
    # two plots next to each other
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    sns.countplot(y=diff_set1_files, ax=ax[0], order=pd.Series(
        diff_set1_files).value_counts().index[:top_k], color=color1)
    ax[0].set_title(f"Top {top_k} files (covered only by {name1})")
    ax[0].set_ylabel('File')
    ax[0].set_xlabel('Count')

    sns.countplot(y=diff_set2_files, ax=ax[1], order=pd.Series(
        diff_set2_files).value_counts().index[:top_k], color=color2)
    ax[1].set_title(f"Top {top_k} files (covered only by {name2})")
    ax[1].set_ylabel('File')
    ax[1].set_xlabel('Count')

    plt.tight_layout()
    plt.show()


# Compare each QITE experiment with each MorphQ experiment
for qite_exp_name, qite_exp_data in package_coverage_ours.items():
    for morphq_exp_name, morphq_exp_data in package_coverage_morphq.items():
        print(f"\nComparing {qite_exp_name} vs {morphq_exp_name}:")

        # Compare covered lines for each platform
        for platform in ['qiskit']:  # PLATFORMS:
            print(f"\n{platform.upper()} COMPARISON:")
            qite_covered = qite_exp_data[platform]["covered_lines"]
            morphq_covered = morphq_exp_data[platform]["covered_lines"]
            print(f"\nCovered lines analysis by file extension:")
            for postfix in ["py", "rs"]:  # Python and Rust files
                print(f"\n{postfix.upper()} files comparison:")
                qite_covered_postfix = [
                    line for line in qite_covered if f".{postfix}:" in line]
                morphq_covered_postfix = [
                    line for line in morphq_covered if f".{postfix}:" in line]
                compare_sets(
                    qite_covered_postfix,
                    morphq_covered_postfix,
                    f"QITE ({qite_exp_name})",
                    f"MorphQ ({morphq_exp_name})",
                    color1="skyblue",
                    color2="lightgreen"
                )


# In[41]:

def print_rust_covered_lines(experiment_data):
    """
    Print covered Rust lines from the experiment coverage data.

    Args:
        experiment_data (dict): Coverage data dictionary containing platform coverage info
    """
    qiskit_covered_lines = experiment_data["qiskit"]["covered_lines"]

    # Filter rust lines
    covered_rust_lines = [
        line for line in qiskit_covered_lines if ".rs:" in line]

    print(f"Total number of covered rust lines: {len(covered_rust_lines)}")

    # Print each rust line with separator
    for line in sorted(covered_rust_lines):
        file_path, line_number = line.split(':')
        file_path = f"qiskit/{file_path}"
        print("-" * 80)
        print(line)

# Example usage for MorphQ data
# morphq_exp_data = package_coverage_morphq[SELECTED_EXP_MORPHQ]
# print("Rust lines covered by MorphQ:")
# print_rust_covered_lines(morphq_exp_data)


# In[11]:


# Styling constants
FIGURE_SIZE = (6, 3)
# light purple, light gray, white
STYLE_COLORS = ['mediumpurple', 'darkgray', 'white']
OUTPUT_IMAGE_PATH = "images/comparison_morphq_covered_lines_venn_w_rust.pdf"


@dataclass
class VennDiagramData:
    """Data structure for Venn diagram components."""
    exclusive_set1: Set[str]
    exclusive_set2: Set[str]
    intersection: Set[str]


def calculate_venn_sets(
    set1: Set[str],
    set2: Set[str],
) -> VennDiagramData:
    """
    Calculate the exclusive and intersection sets for Venn diagram.

    Args:
        set1: First set of lines
        set2: Second set of lines

    Returns:
        VennDiagramData containing exclusive and intersection sets
    """
    return VennDiagramData(
        exclusive_set1=set1 - set2,
        exclusive_set2=set2 - set1,
        intersection=set1 & set2,
    )


def style_venn_diagram(
    venn_plot: Any,
    venn_data: VennDiagramData,
) -> None:
    """
    Apply styling to the Venn diagram components.

    Args:
        venn_plot: Venn diagram plot object
        venn_data: VennDiagramData containing set sizes
    """
    # Set text labels showing set sizes
    venn_plot.get_label_by_id('10').set_text(len(venn_data.exclusive_set1))
    venn_plot.get_label_by_id('01').set_text(len(venn_data.exclusive_set2))
    venn_plot.get_label_by_id('11').set_text(len(venn_data.intersection))

    # Style the diagram sections
    venn_plot.get_patch_by_id('10').set_color(STYLE_COLORS[0])
    venn_plot.get_patch_by_id('01').set_edgecolor(STYLE_COLORS[0])
    venn_plot.get_patch_by_id('01').set_linestyle('dashed')
    venn_plot.get_patch_by_id('01').set_facecolor('white')
    venn_plot.get_patch_by_id('11').set_color(STYLE_COLORS[1])


def create_coverage_venn_diagram(
    qite_lines: Set[str],
    morphq_lines: Set[str],
    qite_label: str = 'QITE',
    morphq_label: str = 'MorphQ',
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create and style a Venn diagram comparing two sets of covered lines.

    Args:
        qite_lines: Set of lines covered by QITE approach
        morphq_lines: Set of lines covered by MorphQ approach
        qite_label: Label for QITE set in diagram
        morphq_label: Label for MorphQ set in diagram

    Returns:
        Figure and Axes objects of the created Venn diagram
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    venn_data = calculate_venn_sets(
        set1=qite_lines,
        set2=morphq_lines,
    )

    venn_plot = venn2(
        subsets=[qite_lines, morphq_lines],
        set_labels=(qite_label, morphq_label),
        ax=ax,
    )
    style_venn_diagram(
        venn_plot=venn_plot,
        venn_data=venn_data,
    )

    plt.show()
    fig.savefig(OUTPUT_IMAGE_PATH)

    return fig, ax, venn_data


def print_latex_commands(
    cov_qiskit_ours: dict,
    cov_qiskit_morphq: dict,
    venn_data: VennDiagramData,
) -> None:
    """
    Print LaTeX commands for coverage statistics.

    Args:
        cov_qiskit_ours: Coverage data from QITE approach
        cov_qiskit_morphq: Coverage data from MorphQ approach
        venn_data: VennDiagramData containing set intersection info
    """
    coverage_commands = [
        ("QITEQiskitCoverage",
            f"{cov_qiskit_ours['coverage_percentage']:.2f}\\%"),
        ("MorphQQiskitCoverage",
            f"{cov_qiskit_morphq['coverage_percentage']:.2f}\\%"),
        ("QITEQiskitTotalLines",
            f"{cov_qiskit_ours['total']}"),
        ("MorphQQiskitTotalLines",
            f"{cov_qiskit_morphq['total']}"),
        ("QITEQiskitCoveredLines",
            f"{cov_qiskit_ours['covered']}"),
        ("MorphQQiskitCoveredLines",
            f"{cov_qiskit_morphq['covered']}"),
        ("CoveredSharedLines", f"{len(venn_data.intersection)}"),
        ("CoveredOnlyQITE", f"{len(venn_data.exclusive_set1)}"),
        ("CoveredOnlyMorphQ", f"{len(venn_data.exclusive_set2)}"),
    ]

    for cmd_name, value in coverage_commands:
        print(f"\\newcommand{{\\{cmd_name}}}{{{value}}}")


exp_morphq = package_coverage_morphq[SELECTED_EXP_MORPHQ]["qiskit"]

for exp_name in SELECTED_EXP_QITE_MULTIPLE:
    print(f"\nCreating Venn diagram for {exp_name}")
    exp_ours = package_coverage_ours[exp_name]["qiskit"]
    # Example usage remains the same but with named arguments
    fig, ax, venn_data = create_coverage_venn_diagram(
        qite_lines=set(exp_ours["covered_lines"]),
        morphq_lines=set(exp_morphq["covered_lines"]),
    )

    print_latex_commands(
        cov_qiskit_ours=exp_ours,
        cov_qiskit_morphq=exp_morphq,
        venn_data=venn_data,
    )


# In[18]:
