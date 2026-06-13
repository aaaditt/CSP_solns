"""
helpers.py — Reusable Utility Functions
========================================
This file is a "toolbox". It contains functions we want to use in multiple
places without copy-pasting code. Instead of rewriting the same logic in
every script, we write it ONCE here and import it anywhere we need it.

How to use these functions in another file:
    from utils.helpers import read_csv, calculate_average

Think of this like a library — you write the books once, then borrow them.
"""

import csv   # built-in Python module for reading/writing CSV files
import json  # built-in Python module for reading/writing JSON files


# ── String Utilities ──────────────────────────────────────────────────────────
# These functions work on text (strings).

def capitalize_words(text):
    """Capitalize every word in a string.
    Example: "hello world" → "Hello World"
    """
    return text.title()  # .title() is a built-in string method


def clean_string(text):
    """Strip whitespace and lowercase a string.
    Example: "  MUMBAI  " → "mumbai"
    Useful when reading messy user input or CSV data.
    """
    return text.strip().lower()  # .strip() removes spaces at edges, .lower() lowercases


# ── Number Utilities ──────────────────────────────────────────────────────────
# These functions do math on lists of numbers.

def calculate_average(numbers):
    """Return the average (mean) of a list of numbers.
    If the list is empty, return 0 instead of crashing.

    How it works:
        average = sum of all values / count of values
        [10, 20, 30] → (10+20+30) / 3 = 20.0
    """
    if not numbers:      # "if not numbers" is True when the list is empty []
        return 0
    return sum(numbers) / len(numbers)
    # sum() adds all items, len() counts them


def find_min_max(numbers):
    """Return a tuple (minimum, maximum) from a list of numbers.
    A tuple is like a list but with exactly 2 values packed together.

    Example: [5, 2, 9, 1] → (1, 9)

    The caller unpacks it like:
        lo, hi = find_min_max([5, 2, 9, 1])
    """
    if not numbers:
        return (None, None)  # return None when there's nothing to compute
    return (min(numbers), max(numbers))


def percentage(part, total):
    """Calculate what percentage 'part' is of 'total'.
    Example: percentage(3, 10) → 30.0

    The round(..., 2) limits decimal places to 2.
    We check for total==0 to avoid ZeroDivisionError.
    """
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


# ── List Utilities ────────────────────────────────────────────────────────────
# These functions manipulate lists.

def flatten_list(nested):
    """Flatten a list of lists into a single flat list.
    Example: [[1, 2], [3, 4], 5] → [1, 2, 3, 4, 5]

    isinstance(item, list) checks if an item IS a list.
    .extend() adds all items from another list into this one.
    .append() adds a single item.
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(item)   # spread inner list into result
        else:
            result.append(item)   # just add the single item
    return result


def remove_duplicates(items):
    """Remove duplicates from a list while preserving the original order.
    Example: ["a", "b", "a", "c", "b"] → ["a", "b", "c"]

    We can't use set() here because sets don't preserve order.
    Instead we track what we've seen manually.
    """
    seen = []
    for item in items:
        if item not in seen:   # only add if we haven't seen it before
            seen.append(item)
    return seen


def filter_by_value(data_list, key, value):
    """Filter a list of dicts, keeping only rows where dict[key] == value.
    Example:
        data = [{"city": "Mumbai"}, {"city": "Delhi"}, {"city": "Mumbai"}]
        filter_by_value(data, "city", "Mumbai")
        → [{"city": "Mumbai"}, {"city": "Mumbai"}]

    This is like a WHERE clause in SQL: SELECT * FROM data WHERE key = value
    """
    # List comprehension: build a new list of items that pass the condition
    return [item for item in data_list if item.get(key) == value]
    # .get(key) is safer than item[key] because it returns None instead of crashing
    # if the key doesn't exist


# ── CSV Utilities ─────────────────────────────────────────────────────────────
# These functions handle reading and writing CSV files.
# CSV = Comma-Separated Values. Just a text file where commas separate columns.
# Example file content:
#   name,age,city
#   Aadit,18,Mumbai
#   Priya,17,Delhi

def read_csv(filepath):
    """Read a CSV file and return a list of dicts (one dict per row).

    csv.DictReader automatically uses the first row as column names (keys).
    So each row becomes: {"name": "Aadit", "age": "18", "city": "Mumbai"}

    Note: ALL values come back as strings — even numbers like "18".
    You have to convert them manually: int(row["age"]) or float(row["score"])

    'with open(...)' automatically closes the file when done — always use this.
    newline="" is required by Python's csv module on Windows.
    encoding="utf-8" handles special characters.
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)   # wraps the file, treats row 1 as headers
        for row in reader:
            rows.append(dict(row))   # convert each row to a plain dict
    return rows


def write_csv(filepath, data, fieldnames=None):
    """Write a list of dicts to a CSV file.

    fieldnames = the list of column headers. If not provided, we take them
    from the first row's keys.

    csv.DictWriter takes dicts and writes them in the correct column order.
    .writeheader() writes the first line (column names).
    .writerows() writes all the data rows.
    """
    if not data:
        print("No data to write.")
        return
    if fieldnames is None:
        fieldnames = list(data[0].keys())   # use keys of first dict as columns
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()    # writes: name,age,city
        writer.writerows(data)  # writes all the data rows
    print(f"Saved {len(data)} rows to {filepath}")


# ── JSON Utilities ────────────────────────────────────────────────────────────
# JSON (JavaScript Object Notation) is a text format for storing structured data.
# It looks almost identical to Python dicts and lists.
# Python dict:  {"name": "Aadit", "scores": [88, 92]}
# JSON string:  {"name": "Aadit", "scores": [88, 92]}
# They look the same but JSON is just text — Python dicts are live objects in memory.

def read_json(filepath):
    """Read a JSON file and return the parsed Python object (dict or list).
    json.load() reads from a file object and converts JSON → Python.
    """
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)   # converts JSON text into Python dict/list


def write_json(filepath, data, indent=2):
    """Write a Python object (dict or list) to a JSON file.
    json.dump() converts Python → JSON and writes to a file.
    indent=2 makes the file human-readable with 2-space indentation.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    print(f"Saved JSON to {filepath}")


def dict_to_json_string(data):
    """Convert a Python dict to a formatted JSON string (not a file).
    json.dumps() = "dump to string" (the 's' stands for string).
    json.dump()  = "dump to file".
    """
    return json.dumps(data, indent=2)


# ── Display Utilities ─────────────────────────────────────────────────────────
# These functions make terminal output look cleaner and easier to read.

def print_separator(title="", char="-", width=50):
    """Print a visual separator line with an optional title.
    Example output:
        --- Score Summary ---------------------------------

    This is purely cosmetic — makes the output easier to read.
    """
    if title:
        # f-string: repeats char 3 times, adds title, then fills the rest
        print(f"\n{char * 3} {title} {char * (width - len(title) - 5)}")
    else:
        print(char * width)


def print_table(data, columns=None):
    """Print a list of dicts as a neatly aligned table in the terminal.

    How it works:
    1. Calculate the maximum width needed for each column
    2. Print the header row
    3. Print a separator line
    4. Print each data row, with each cell padded to the right width

    .ljust(width) = "left justify" — pads text with spaces on the right
    so all cells in the same column line up perfectly.
    """
    if not data:
        print("No data to display.")
        return
    if columns is None:
        columns = list(data[0].keys())   # use all columns if none specified

    # Step 1: find the widest value in each column (including the header name)
    widths = {col: len(col) for col in columns}  # start with header widths
    for row in data:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    # Step 2: print header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    print(header)
    print("-" * len(header))  # separator line under header

    # Step 3: print each row
    for row in data:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        print(line)
