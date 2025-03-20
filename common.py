"""
A set of common consts, functions, and other useful items that are common to all Python-related
assignment files.

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

# type definitions
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


def get_csv_headers(header_row: list[str], required_headers: list[str]) -> CsvHeaders:
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
    if not all((header in header_row) for header in required_headers):
        raise ValueError("CSV is missing one or more required headers; expected all of '"
                         + "', '".join(str(header) for header in required_headers) + "'")
    csv_headers: CsvHeaders = {}
    for header in required_headers:
        csv_headers[header] = header_row.index(header)
    return csv_headers


def read_csv(csv_path: str, required_headers: list[str], delimiter: str=DEFAULT_DELIMITER) \
        -> tuple[CsvHeaders, Csv]:
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
    return get_csv_headers(header_row, required_headers), csv_rows


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


if __name__ == '__main__':
    print("This file is not intended to be run on its own.\n"
          "Please see README for more information.")
    sys.exit(1)
