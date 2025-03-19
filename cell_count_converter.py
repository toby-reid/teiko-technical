#!/usr/bin/env python3

"""
Converts cell count in a CSV to relative frequency of total call count.

Answers Question 1 in the Python section of the assignment.

Author: Toby Reid
"""

import argparse
import csv
from enum import StrEnum
import os
import sys


ENCODING = "utf-8-sig"
DEFAULT_DELIMITER = ','

CELL_TYPES = StrEnum("Immune Cell Types", [
    "B_CELL",
    "CD8_T_CELL",
    "CD4_T_CELL",
    "NK_CELL",
    "MONOCYTE",
])

SAMPLE_HEADER = "sample"

# If this order is updated, the order in `get_output_csv_row` will also need to be updated.
OUTPUT_HEADERS = StrEnum("Output CSV Headers", [
    SAMPLE_HEADER.upper(),
    "TOTAL_COUNT",
    "POPULATION",
    "COUNT",
    "PERCENTAGE",
])

CsvHeaders = dict[str, int]
Csv = list[list[str]]


class ExpandPathAction(argparse.Action):
    """An `argparse` action that will expand any number of given paths into a full absolute path."""
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            raise SyntaxError("ExpandPathAction used incorrectly; requires at least 1 input")
        if isinstance(values, str):
            path = os.path.abspath(os.path.expandvars(os.path.expanduser(values)))
            setattr(namespace, self.dest, path)
        else:
            paths = [os.path.abspath(os.path.expandvars(os.path.expanduser(value)))
                     for value in values]
            setattr(namespace, self.dest, paths)


class ValidatePathAction(ExpandPathAction):
    """An `argparse` action that will ensure the given value (only 1) is an existing path."""
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str) or not os.path.exists(values):
            raise ValueError(f"{values} is not a valid path")
        super().__call__(parser, namespace, values, option_string)


def get_csv_headers(header_row: list[str]) -> CsvHeaders:
    """
    Extracts the indices of the headers required for this module from the given Header row.

    Parameters:
        header_row (list[str]): The original CSV's header row, which should contain all required \
                                headers

    Returns:
        CsvHeaders: A mapping of header names to their respective indices

    Raises:
        ValueError: if the provided header row is missing any required headers
    """
    required_headers = [SAMPLE_HEADER] + list(CELL_TYPES)
    if not all((header in header_row) for header in required_headers):
        raise ValueError("CSV is missing one or more required headers; expected all of "
                         f"{required_headers}")
    csv_headers: CsvHeaders = {}
    for header in required_headers:
        csv_headers[header] = header_row.index(header)
    return csv_headers


def read_csv(csv_path: str, delimiter: str=DEFAULT_DELIMITER) -> tuple[CsvHeaders, Csv]:
    """
    Reads a CSV file and validates its header row.

    Args:
        csv_path (str):  The file path to the CSV file to be read
        delimiter (str): The delimiter used in the CSV file

    Returns:
        tuple[CsvHeaders, Csv]: A tuple containing the headers and the rows of the CSV file

    Raises:
        ValueError: If the CSV file is empty or is missing required headers
    """
    with open(csv_path, 'r', encoding=ENCODING, newline='') as file:
        reader = csv.reader(file, delimiter=delimiter)
        csv_rows = list(reader)
    if not csv_rows:
        raise ValueError(f"Failed to parse empty CSV: {csv_path}")

    header_row = csv_rows.pop(0)
    return get_csv_headers(header_row), csv_rows


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


def write_csv(output_file: str | None, output_csv: Csv, delimiter: str=DEFAULT_DELIMITER) -> None:
    """
    Writes the given CSV to the specified file, or to stdout if no file is specified.

    Args:
        output_file (str | None):
            str:  The file path to write the output CSV <br/>
            None: to write to stdout
        output_csv (Csv):         The CSV data to write
        delimiter (str):          The delimiter to use in the output CSV
    """
    if output_file is None:
        writer = csv.writer(sys.stdout, delimiter=delimiter)
        writer.writerows(output_csv)
    else:
        with open(output_file, 'w', encoding=ENCODING, newline='') as file:
            writer = csv.writer(file, delimiter=delimiter)
            writer.writerows(output_csv)
        print(f"Wrote output CSV to {output_file}")


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
    csv_headers, csv_rows = read_csv(arg_values.csv_file, delimiter=arg_values.delimiter)
    output_csv = convert_cell_count(csv_headers, csv_rows)
    write_csv(arg_values.output, output_csv, delimiter=arg_values.delimiter)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
