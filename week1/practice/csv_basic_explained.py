# =============================================================================
# CSV Basic Analyzer — Fully Explained Version
# =============================================================================
# This is a simplified CSV analyzer that does just two things:
#   1. Loads a CSV file
#   2. Prints a summary (shape, data types, missing values, numeric stats)
#
# No menu system, no filtering, no sorting, no exporting.
# Great for learning the basics of pandas before moving to the full version.
#
# To run:  python csv_basic_explained.py
# =============================================================================

# pandas is a library for working with tables of data (called DataFrames).
# We import it as "pd" so we can write pd.read_csv() instead of pandas.read_csv().
import pandas as pd


# =============================================================================
# FUNCTION 1: load_csv
# =============================================================================
# This function takes a file path, reads the CSV, and returns the data.
#
# Key concepts:
#   - pd.read_csv(filepath) reads a CSV file and turns it into a DataFrame.
#     A DataFrame is like a spreadsheet — rows and columns of data.
#   - try/except catches errors so the program doesn't crash if the file
#     is missing or unreadable.
#   - We return None if something goes wrong, so the calling code can check.
# =============================================================================
def load_csv(filepath):
    """Loads a CSV file and returns a DataFrame."""
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(filepath)

        # df.shape is a tuple: (number_of_rows, number_of_columns)
        # shape[0] = rows, shape[1] = columns
        print(f"\nLoaded '{filepath}' — {df.shape[0]} rows, {df.shape[1]} columns.\n")
        return df

    except FileNotFoundError:
        # The file path the user typed doesn't point to a real file
        print(f"\nError: File '{filepath}' not found.\n")
        return None

    except Exception as e:
        # Catch-all for any other unexpected error
        # 'e' holds the error message
        print(f"\nError: {e}\n")
        return None


# =============================================================================
# FUNCTION 2: summarize
# =============================================================================
# This prints everything you'd want to know about the data at a glance:
#
#   1. Shape — how many rows and columns
#   2. Column names — what the data fields are called
#   3. Data types — what kind of data each column holds:
#        - int64   = whole numbers (1, 2, 3)
#        - float64 = decimal numbers (3.14, 75000.0)
#        - object/str = text ("Alice", "Engineering")
#   4. Missing values — how many empty cells per column
#        - In pandas, empty cells become NaN (Not a Number)
#        - df.isnull() marks True for every NaN cell
#        - .sum() counts how many Trues (= how many missing)
#   5. Numeric statistics — min, max, mean, median for number columns
#        - min = smallest value
#        - max = largest value
#        - mean = average (total / count)
#        - median = middle value when sorted
# =============================================================================
def summarize(df):
    """Prints a summary of the DataFrame — shape, types, missing values, and basic stats."""
    print("=" * 50)
    print("  DATA SUMMARY")
    print("=" * 50)

    # Print the number of rows and columns
    print(f"\nRows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # df.columns is a list of all column names
    # ', '.join() turns the list into a comma-separated string
    print(f"Column Names: {', '.join(df.columns)}")

    # Print the data type of each column
    print("\nData Types:")
    for col in df.columns:
        # df[col].dtype gives the type (int64, float64, object, etc.)
        print(f"  {col} -> {df[col].dtype}")

    # Count and print missing values per column
    # df.isnull().sum() returns a series with the count of NaN per column
    # .items() lets us loop through column-name, count pairs
    print("\nMissing Values:")
    for col, count in df.isnull().sum().items():
        print(f"  {col} -> {count}")

    # Filter to only numeric columns so we can calculate stats
    # select_dtypes(include="number") keeps only int and float columns
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        print("\nNumeric Stats:")
        for col in numeric_cols:
            # For each numeric column, print the four key statistics
            # :.2f means "format as a float with 2 decimal places"
            # NaN values are automatically skipped by min/max/mean/median
            print(f"\n  {col}:")
            print(f"    Min:    {df[col].min():.2f}")
            print(f"    Max:    {df[col].max():.2f}")
            print(f"    Mean:   {df[col].mean():.2f}")
            print(f"    Median: {df[col].median():.2f}")

    print("\n" + "=" * 50)


# =============================================================================
# FUNCTION 3: main
# =============================================================================
# This is the entry point. It:
#   1. Asks the user to type a file path
#   2. Tries to load it
#   3. If it worked, prints the summary
#
# input() pauses and waits for the user to type something.
# .strip() removes extra spaces or newlines from what they typed.
# =============================================================================
def main():
    """Asks for a CSV file path, loads it, and prints the summary."""
    filepath = input("Enter CSV file path: ").strip()
    df = load_csv(filepath)

    # If load_csv returned None, the file couldn't be loaded, so we stop
    if df is not None:
        summarize(df)


# =============================================================================
# This checks if the script is being run directly (not imported).
# If you run "python csv_basic_explained.py", __name__ is "__main__" so
# main() gets called. If another script imports this file, main() won't
# run automatically — they can just use load_csv() and summarize() directly.
# =============================================================================
if __name__ == "__main__":
    main()
