"""
csv_analyzer.py — Main Deliverable Script
==========================================
This is a proper Python SCRIPT — it runs from top to bottom when you execute it.
Unlike a Jupyter notebook (where you run cells one at a time), a script runs
all at once when you type:

    python scripts/csv_analyzer.py

This script reads two CSV files, analyzes the data, and prints reports.
It uses the helper functions we wrote in utils/helpers.py so we don't
repeat code.

HOW IMPORTS WORK:
-----------------
Python looks for modules in specific folders. Since csv_analyzer.py lives
in scripts/ and helpers.py lives in utils/, we have to tell Python where
to look using sys.path.append() — it adds a folder to Python's search list.

Without that, "from utils.helpers import ..." would fail with ModuleNotFoundError.
"""

import sys    # sys = system module, lets us modify Python's behaviour
import os     # os = operating system module, lets us work with file paths

# This line tells Python: "also look for modules in the parent folder (week1/)"
# os.path.abspath(__file__)  → full path of THIS file (csv_analyzer.py)
# os.path.dirname(...)       → folder containing this file (scripts/)
# os.path.dirname(...again)  → parent folder of that (week1/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now Python can find utils/helpers.py because week1/ is in the search path
from utils.helpers import (
    read_csv,
    write_csv,
    calculate_average,
    find_min_max,
    percentage,
    filter_by_value,
    print_separator,
    print_table,
)


# ── Analysis Functions ────────────────────────────────────────────────────────
# These are helper functions SPECIFIC to this script (not general-purpose enough
# to go in helpers.py). They each do one clear job.

def summarize_numeric_column(data, column):
    """Print summary statistics for one numeric column across all rows.

    'data' is a list of dicts (what read_csv returns).
    'column' is the name of the column we want to analyze, e.g. "score".

    We loop through every row, try to convert the value to a float,
    and skip anything that isn't a valid number.
    """
    values = []
    for row in data:
        try:
            values.append(float(row[column]))  # CSV values are strings, float() converts them
        except (ValueError, KeyError):
            pass  # ValueError: "abc" can't become a float. KeyError: column doesn't exist.
            # 'pass' means "do nothing and move on" — we just skip bad rows

    if not values:
        print(f"  No numeric data found in column '{column}'")
        return

    avg = calculate_average(values)
    mn, mx = find_min_max(values)   # unpacks the (min, max) tuple
    total = sum(values)

    print(f"  Column   : {column}")
    print(f"  Count    : {len(values)}")
    print(f"  Total    : {total}")
    print(f"  Average  : {avg:.2f}")   # :.2f means "show 2 decimal places"
    print(f"  Min      : {mn}")
    print(f"  Max      : {mx}")


def count_by_column(data, column):
    """Count how many rows share each unique value in a column.
    Returns a dictionary where keys are unique values and values are counts.

    Example:
        data has 3 Mumbai rows and 2 Delhi rows
        returns: {"Mumbai": 3, "Delhi": 2}

    This pattern — building a count dictionary — is extremely common in data work.
    It's called "grouping" or "frequency counting".
    """
    counts = {}   # empty dict, we'll fill it as we loop

    for row in data:
        val = row.get(column, "Unknown")   # get value, default to "Unknown" if missing
        # counts.get(val, 0) → look up current count, default to 0 if not seen yet
        # then add 1 to it
        counts[val] = counts.get(val, 0) + 1

    return counts


def find_top_n(data, column, n=3, highest=True):
    """Return the top N rows sorted by a numeric column.

    sorted() sorts a list. The key= argument tells it WHAT to sort by.
    lambda row: float(row.get(column, 0))
        → for each row, extract the numeric value of 'column'

    reverse=True  → largest first (descending)
    reverse=False → smallest first (ascending)

    [:n] slices the first n items from the sorted list.
    """
    try:
        sorted_data = sorted(
            data,
            key=lambda row: float(row.get(column, 0)),
            reverse=highest
        )
        return sorted_data[:n]   # return only the first n rows
    except ValueError:
        print(f"  Column '{column}' has non-numeric values, can't sort.")
        return []


# ── Report Functions ──────────────────────────────────────────────────────────
# Each function below reads one CSV file, runs several analyses, and prints
# a complete report. These are the "main" functions of this script.

def analyze_students():
    """Run the full students report."""

    # Build the path to the CSV file relative to this script's location.
    # os.path.join() builds file paths correctly on any operating system
    # (Windows uses \, Mac/Linux use / — os.path.join handles it automatically)
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "students.csv")
    data = read_csv(filepath)   # returns a list of dicts

    print_separator("STUDENTS REPORT")
    print(f"Total students loaded: {len(data)}\n")

    print_separator("All Students")
    print_table(data)   # prints a formatted table of all rows

    print_separator("Score Statistics")
    summarize_numeric_column(data, "score")

    print_separator("Students per City")
    city_counts = count_by_column(data, "city")   # {"Mumbai": 3, "Delhi": 2, ...}
    for city, count in sorted(city_counts.items()):
        # sorted() on a dict's .items() sorts alphabetically by key (city name)
        bar = "#" * count   # visual bar: Mumbai ### means 3 students
        print(f"  {city:<12} {bar} ({count})")
        # {city:<12} = left-align city name in a 12-character wide column

    print_separator("Top 3 Scorers")
    top3 = find_top_n(data, "score", n=3, highest=True)
    print_table(top3)

    print_separator("Students from Mumbai")
    mumbai = filter_by_value(data, "city", "Mumbai")
    print_table(mumbai)

    # Save the filtered results to a NEW CSV file
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "mumbai_students.csv")
    write_csv(out_path, mumbai)
    # After running this script, check data/mumbai_students.csv — it will exist!


def analyze_products():
    """Run the full products report."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "products.csv")
    data = read_csv(filepath)

    print_separator("PRODUCTS REPORT")
    print(f"Total products loaded: {len(data)}\n")

    print_separator("All Products")
    print_table(data)

    print_separator("Price Statistics")
    summarize_numeric_column(data, "price")

    print_separator("Products per Category")
    cat_counts = count_by_column(data, "category")
    for cat, count in sorted(cat_counts.items()):
        pct = percentage(count, len(data))   # e.g. 4 out of 10 = 40.0%
        print(f"  {cat:<15} {count} products ({pct}%)")

    print_separator("Top 3 Highest Rated Products")
    top_rated = find_top_n(data, "rating", n=3, highest=True)
    # columns= lets us show only specific columns in the table (not all of them)
    print_table(top_rated, columns=["product_name", "category", "rating"])

    print_separator("Electronics Only")
    electronics = filter_by_value(data, "category", "Electronics")
    print_table(electronics)


# ── Entry Point ───────────────────────────────────────────────────────────────
# This is a Python convention. When you RUN this file directly:
#     python scripts/csv_analyzer.py
# Python sets __name__ to "__main__".
#
# When some OTHER file IMPORTS this file:
#     from scripts.csv_analyzer import analyze_students
# Python sets __name__ to "csv_analyzer" — and the block below does NOT run.
#
# This pattern lets a file be both importable (as a module) and runnable
# (as a script), without accidentally running code on import.

if __name__ == "__main__":
    analyze_students()
    print("\n")
    analyze_products()
    print_separator("Analysis Complete")
