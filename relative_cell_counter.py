#!/usr/bin/env python3

"""
Converts cell count in a CSV to relative frequency of total call count.

Answers Question 1 in the Python section of the assignment.

Author: Toby Reid
"""

import argparse
from enum import StrEnum
import sys

from common import CELL_TYPES, DEFAULT_DELIMITER, SAMPLE_HEADER, Csv, CsvHeaders, \
    ExpandPathAction, ValidatePathAction, read_csv, write_csv


# If this order is updated, the order in `get_output_csv_row` will also need to be updated.
OUTPUT_HEADERS = StrEnum("Output CSV Headers", [
    SAMPLE_HEADER.upper(),
    "TOTAL_COUNT",
    "POPULATION",
    "COUNT",
    "PERCENTAGE",
])


def get_output_csv_row(sample: str, total_count: int, population: str, count: int) -> list[str]:
    """
    Generates a single row for the output CSV.

    Args:
        sample (str):      The sample ID
        total_count (int): The total cell count for the entire sample
        population (str):  The name of the individual immune cell population
        count (int):       The cell count for the population

    Returns:
        list[str]: A row for the output CSV
    """
    percentage = (count / total_count) * 100
    return [sample, str(total_count), population, str(count), f"{percentage:.2f}"]


def convert_sample_cell_count(csv_headers: CsvHeaders, csv_row: list[str]) -> Csv:
    """
    Converts a single sample into rows with relative cell counts for individual populations.

    Args:
        csv_headers (CsvHeaders): A mapping of header names to their respective indices
        csv_row (list[str]):      A single row from the input CSV

    Returns:
        Csv: A list of rows for the output CSV
    """
    total_count = 0
    cell_counts: dict[CELL_TYPES, int] = {}
    for cell_type in CELL_TYPES:
        # Allow it to throw an Error if casting to int fails
        cell_count = int(csv_row[csv_headers[cell_type]])
        total_count += cell_count
        cell_counts[cell_type] = cell_count

    output_rows: Csv = []
    sample = csv_row[csv_headers[SAMPLE_HEADER]]
    for cell_type in CELL_TYPES:
        output_rows.append(get_output_csv_row(sample, total_count, cell_type,
                                              cell_counts[cell_type]))
    return output_rows


def convert_cell_count(csv_headers: CsvHeaders, csv_rows: Csv) -> Csv:
    """
    Converts a CSV into a new CSV with relative cell counts for individual populations.

    Args:
        csv_headers (CsvHeaders): A mapping of header names to their respective indices
        csv_rows (Csv):           The input CSV

    Returns:
        Csv: The completed output CSV
    """
    output_csv: Csv = [list(OUTPUT_HEADERS)]
    for csv_row in csv_rows:
        output_csv.extend(convert_sample_cell_count(csv_headers, csv_row))
    return output_csv


def parse_args(args: list[str]) -> argparse.Namespace:
    """
    Parses command-line arguments for this tool.

    Args:
        args (list[str]): The list of command-line arguments (not including this file's name)

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=("Reads and converts total cell count in a CSV to relative frequency of total "
                     "cell count.")
    )
    parser.add_argument(
        "csv_file",
        action=ValidatePathAction,
        help="The CSV file to parse",
    )
    parser.add_argument(
        "-o", "--output",
        action=ExpandPathAction,
        help="The file to which CSV output should be written",
    )
    parser.add_argument(
        "-d", "--delimiter",
        default=DEFAULT_DELIMITER,
        help="The delimiter used in the given CSV, and to use in the output CSV",
    )
    return parser.parse_args(args)


def main(args: list[str]) -> int:
    """
    Entry point for the cell count transformer script.

    Args:
        args (list[str]): Command-line arguments passed to the script (not including this file)

    Returns:
        int: Exit code of the script (0 on success)
    """
    arg_values = parse_args(args)
    required_headers = [SAMPLE_HEADER] + CELL_TYPES
    csv_headers, csv_rows = read_csv(arg_values.csv_file, required_headers,
                                     delimiter=arg_values.delimiter)
    output_csv = convert_cell_count(csv_headers, csv_rows)
    write_csv(arg_values.output, output_csv, delimiter=arg_values.delimiter)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
