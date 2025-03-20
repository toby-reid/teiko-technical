#!/usr/bin/env python3

"""
Analyzes cell counts compared with treatment effectiveness and makes a box plot thereof.

Answers Question 2 in the Python section of the assignment.

Author: Toby Reid
"""

import argparse
import os
import sys

from matplotlib import pyplot
from matplotlib.figure import Figure as PyplotFigure

from common import CELL_TYPES, DEFAULT_DELIMITER, SAMPLE_HEADER, Csv, CsvHeaders, \
    ValidatePathAction, ExpandPathAction, get_csv_headers, read_csv, write_csv
from relative_cell_counter import convert_cell_count
from relative_cell_counter import OUTPUT_HEADERS as RELATIVE_HEADERS


TREATMENT_HEADER = "treatment"
TREATMENT = "tr1"

SAMPLE_TYPE_HEADER = "sample_type"
INCLUDE_SAMPLE_TYPES = ("PBMC",)

RESPONSE_HEADER = "response"
RESPONDING = "y"
NONRESPONDING = "n"


# 2. Among patients who have treatment tr1, we are interested in comparing the differences in cell
# population relative frequencies of melanoma patients who respond (responders) to tr1 versus those
# who do not (non-responders), with the overarching aim of predicting response to treatment tr1.
# Response information can be found in column response, with value y for responding and value n for
# non-responding. Please only include PBMC (blood) samples.

# a. For each immune cell population, please generate a boxplot of the population relative
# frequencies comparing responders versus non-responders.

# b. Which cell populations are significantly different in relative frequencies between responders
# and non-responders? Please include statistics to support your conclusion.


def get_sample_relative(relative_headers: CsvHeaders, relative_csv: Csv, sample_id: str) \
        -> dict[CELL_TYPES, float]:
    """
    Retrieves all relative percentages of a given sample for each of the cell type populations.

    Args:
        relative_headers (CsvHeaders): A mapping of header names to their respective indices
        relative_csv (Csv):            The CSV containing the relative cell counts
        sample_id (str):               The sample name for which to retrieve the relative counts

    Returns:
        dict[CELL_TYPES, float]: A mapping of cell types to their respective relative percentages
    """
    sample_responders: dict[CELL_TYPES, float] = {}
    for csv_row in relative_csv:
        if csv_row[relative_headers[SAMPLE_HEADER]] == sample_id:
            cell_type = csv_row[relative_headers[RELATIVE_HEADERS.POPULATION]]
            if sample_responders.get(cell_type):
                raise ValueError("Given CSV is invalid; expected 1 entry per population, per "
                                 f"sample, but got multiple entries for sample {sample_id} with "
                                 f"population {cell_type}")
            population_percentage = float(csv_row[relative_headers[RELATIVE_HEADERS.PERCENTAGE]])
            sample_responders[cell_type] = population_percentage
    return sample_responders


def calculate_responders(treatment_headers: CsvHeaders, treatment_csv: Csv,
                         relative_headers: CsvHeaders, relative_csv: Csv) \
        -> tuple[dict[CELL_TYPES, list[float]], dict[CELL_TYPES, list[float]]]:
    """
    Locates all data points for responders and non-responders for each data type within the given
    treatment data.

    Args:
        treatment_headers (CsvHeaders): A mapping of header names to their respective indices
        treatment_csv (Csv):            The CSV containing the treatment data
        relative_headers (CsvHeaders):  A mapping of header names to their respective indices
        relative_csv (Csv):             The CSV containing the relative cell counts

    Returns:
        tuple[dict[CELL_TYPES, list[float]], dict[CELL_TYPES, list[float]]]:
            responders:    A mapping of cell types to lists of relative counts samples where the \
                           data indicate a response
            nonresponders: A mapping of cell types to lists of relative counts samples where the \
                           data indicate no response
    """
    population_responders: dict[CELL_TYPES, list[float]] = {}
    population_nonresponders: dict[CELL_TYPES, list[float]] = {}
    for cell_type in CELL_TYPES:
        population_responders[cell_type] = []
        population_nonresponders[cell_type] = []

    for sample in treatment_csv:
        if sample[treatment_headers[TREATMENT_HEADER]] == TREATMENT \
                and sample[treatment_headers[SAMPLE_TYPE_HEADER]] in INCLUDE_SAMPLE_TYPES:
            sample_id = sample[treatment_headers[SAMPLE_HEADER]]
            sample_relative_count = get_sample_relative(relative_headers, relative_csv, sample_id)
            # Select which counter to use, based on whether the sample is a responder
            population_counter = \
                population_responders if sample[treatment_headers[RESPONSE_HEADER]] == RESPONDING \
                else population_nonresponders
            for cell_type, relative_count in sample_relative_count.items():
                population_counter[cell_type].append(relative_count)

    return population_responders, population_nonresponders


def generate_boxplot(label: str, responders: list[float], nonresponders: list[float]) \
        -> PyplotFigure:
    """
    Generates a singular boxplot comparing the relative cell counts of a cell type, showing both
    responders and nonresponders.

    Args:
        label (str):                 The label to use for the plot (the cell type)
        responders (list[float]):    The relative cell counts for responders
        nonresponders (list[float]): The relative cell counts for nonresponders

    Returns:
        PyplotFigure: The generated boxplot
    """
    figure, axes = pyplot.subplots()
    # Builds from the bottom up, so put nonresponders first to responders is on top
    axes.boxplot([nonresponders, responders], vert=False,
                 tick_labels=["nonresponders", f"{TREATMENT} responders"])
    axes.set_title(label)
    axes.set_xlabel("Percentage of cells of this type within sample")
    figure.tight_layout()
    return figure


def generate_boxplots(treatment_headers: CsvHeaders, treatment_csv: Csv,
                      relative_headers: CsvHeaders, relative_csv: Csv) \
        -> dict[CELL_TYPES, PyplotFigure]:
    """
    Calculates and generates boxplots for each cell type, comparing responders and nonresponders.

    Args:
        treatment_headers (CsvHeaders): A mapping of header names to their respective indices
        treatment_csv (Csv):            The CSV containing the treatment data
        relative_headers (CsvHeaders):  A mapping of header names to their respective indices
        relative_csv (Csv):             The CSV containing the relative cell counts

    Returns:
        dict[CELL_TYPES, PyplotFigure]: A mapping of cell types to their respective boxplots
    """
    responders, nonresponders = calculate_responders(treatment_headers, treatment_csv,
                                                     relative_headers, relative_csv)
    boxplots: dict[CELL_TYPES, PyplotFigure] = {}
    for cell_type in CELL_TYPES:
        boxplots[cell_type] = generate_boxplot(cell_type, responders[cell_type],
                                               nonresponders[cell_type])
    return boxplots


def parse_args(args: list[str]) -> argparse.Namespace:
    """
    Parses command-line arguments for this tool.

    Args:
        args (list[str]): The command-line arguments (not including this file's name)

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=("Reads and interprets cell counts compared to treatment effectiveness in "
                     "various samples, creating a box plot to help in analyzation."),
        epilog=("If a relative cell count (percentage) CSV is not provided, the relative cell "
                "counter tool will be used to generate one in the process.")
    )
    parser.add_argument(
        "treatment_csv",
        action=ValidatePathAction,
        help="The CSV file containing treatment and cell count data (e.g., cell-count.csv)",
    )
    parser.add_argument(
        "-r", "--relative-csv",
        action=ExpandPathAction,
        nargs='?',  # the argument is optional
        help=("A CSV file containing relative cell counts, as generated by relative_cell_counter. "
              "If the file does not exist, it will be created"),
    )
    parser.add_argument(
        "-b", "--boxplot-dir",
        action=ExpandPathAction,
        help=("The directory under which to save the generated boxplots. If none is provided, "
              "it will just be displayed to the user in separate windows"),
    )
    parser.add_argument(
        "-d", "--delimiter",
        default=DEFAULT_DELIMITER,
        help=("The delimiter used in the given CSV, and to use in the output CSV (default is '"
              f"{DEFAULT_DELIMITER}')"),
    )
    arg_values = parser.parse_args(args)
    # Ensure that, if given a boxplot directory, we don't try to treat an existing file like a
    # directory
    if arg_values.boxplot_dir \
            and os.path.exists(arg_values.boxplot_dir) \
            and not os.path.isdir(arg_values.boxplot_dir):
        print(f"Warning: Can not save boxplots to {arg_values.boxplot_dir}, as it already exists "
              "but is not a directory.", file=sys.stderr)
        arg_values.boxplot_dir = None  # Display the plots in windows instead, like the default
    return arg_values


def main(args: list[str]) -> int:
    """
    Entry point for the cell treatment analyzer script.

    Args:
        args (list[str]): Command-line arguments passed to the script (not including this file)

    Returns:
        int: Exit code of the script (0 on success)
    """
    arg_values = parse_args(args)
    required_headers = [SAMPLE_HEADER, TREATMENT_HEADER, SAMPLE_TYPE_HEADER, RESPONSE_HEADER] \
                       + list(CELL_TYPES)
    treatment_headers, treatment_csv = read_csv(arg_values.treatment_csv, required_headers,
                                                delimiter=arg_values.delimiter)

    if not arg_values.relative_csv or not os.path.isfile(arg_values.relative_csv):
        # Make our own CSV
        relative_csv = convert_cell_count(treatment_headers, treatment_csv)
        relative_headers = get_csv_headers(relative_csv.pop(0), RELATIVE_HEADERS)
        if arg_values.relative_csv:
            if not os.path.exists(arg_values.relative_csv):
                file_csv = [RELATIVE_HEADERS] + relative_csv
                write_csv(arg_values.relative_csv, file_csv, delimiter=arg_values.delimiter)
            else:
                print(f"Couldn't write CSV file {arg_values.relative_csv} as the path already "
                      "exists, yet is not a file", file=sys.stderr)
    else:
        # We were provided with a CSV
        relative_headers, relative_csv = read_csv(arg_values.relative_csv,
                                                  RELATIVE_HEADERS,
                                                  delimiter=arg_values.delimiter)

    boxplots = generate_boxplots(treatment_headers, treatment_csv, relative_headers, relative_csv)
    if arg_values.boxplot_dir:
        os.makedirs(arg_values.boxplot_dir, exist_ok=True)
        for cell_type, boxplot in boxplots.items():
            file_path = os.path.join(arg_values.boxplot_dir, f"{cell_type}.png")
            boxplot.savefig(file_path)
            print(f"Saved {cell_type} plot as {file_path}")
    else:
        print("Displaying all charts in separate windows")
        pyplot.show()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
