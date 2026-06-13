# =============================================================================
# CSV Analyzer Script — Fully Explained Version
# =============================================================================
#
# This script reads a CSV file, shows a summary of the data, and lets the user
# filter, sort, and export data through a simple text-based menu.
#
# Only external library needed: pandas (install with: pip install pandas)
#
# How to run:
#   python csv_analyzer_explained.py
#
# It will ask you for a CSV file path, then show a menu with options.
# =============================================================================

# We import pandas, which is a powerful library for working with tabular data.
# We give it the alias "pd" so we can write pd.read_csv() instead of pandas.read_csv().
import pandas as pd


# =============================================================================
# FUNCTION 1: load_csv
# =============================================================================
# Purpose: Takes a file path as input, tries to read the CSV file using pandas,
#          and returns the data as a DataFrame (basically a table in memory).
#
# Why try/except? — The file might not exist, might be empty, or could have some
#          other issue. try/except lets us catch those errors and show a friendly
#          message instead of crashing the whole program.
#
# What is a DataFrame? — Think of it like an Excel spreadsheet stored in Python.
#          Each column has a name, each row has data. You can filter, sort, and
#          do math on it easily.
# =============================================================================
def load_csv(filepath):
    """Loads a CSV file into a DataFrame and returns it."""

    try:
        # pd.read_csv() reads the CSV file and converts it into a DataFrame.
        # If the file doesn't exist, Python will raise a FileNotFoundError.
        df = pd.read_csv(filepath)

        # df.shape gives us a tuple like (15, 6) meaning 15 rows, 6 columns.
        # shape[0] = number of rows, shape[1] = number of columns.
        print(f"\n[OK] Successfully loaded '{filepath}' ({df.shape[0]} rows, {df.shape[1]} columns).\n")
        return df

    except FileNotFoundError:
        # This runs if the file path doesn't point to a real file.
        print(f"\n[ERROR] File '{filepath}' was not found. Please check the path and try again.\n")
        return None

    except pd.errors.EmptyDataError:
        # This runs if the file exists but has no data in it at all.
        print(f"\n[ERROR] File '{filepath}' is empty.\n")
        return None

    except Exception as e:
        # This catches ANY other error we didn't specifically plan for.
        # The variable 'e' holds the error message so we can print it.
        print(f"\n[ERROR] Error reading file: {e}\n")
        return None


# =============================================================================
# FUNCTION 2: summarize
# =============================================================================
# Purpose: Prints out a detailed summary of the data:
#   - How many rows and columns
#   - What the columns are called
#   - What data type each column holds (text, integer, decimal, etc.)
#   - How many values are missing in each column
#   - For numeric columns: the minimum, maximum, average, and median values
#
# What are data types?
#   - "int64" means whole numbers (like 29, 42)
#   - "float64" means decimal numbers (like 75000.0, 4.2)
#   - "object" or "str" means text/string data (like "Alice", "Engineering")
#
# What is a "missing value"?
#   - If a cell in the CSV is empty, pandas stores it as NaN (Not a Number).
#   - df.isnull().sum() counts how many NaN values each column has.
# =============================================================================
def summarize(df):
    """Prints a full summary of the dataframe including shape, types, missing values, and numeric stats."""

    print("\n" + "=" * 60)
    print("                   DATA SUMMARY")
    print("=" * 60)

    # --- Number of rows and columns ---
    # df.shape returns a tuple like (15, 6).
    # We unpack it into two variables: rows and cols.
    rows, cols = df.shape
    print(f"\nRows    : {rows}")
    print(f"Columns : {cols}")

    # --- Column names ---
    # df.columns gives us a list of all column names.
    # ', '.join() combines them into a single string separated by commas.
    print(f"\nColumn Names:\n  {', '.join(df.columns)}")

    # --- Data types ---
    # df[col].dtype tells us the type of data in that column.
    # We loop through every column and print its type.
    print("\nData Types:")
    for col in df.columns:
        # The :30s means "pad the string to 30 characters wide" for alignment.
        print(f"  {col:30s} -> {df[col].dtype}")

    # --- Missing values ---
    # df.isnull() returns True/False for every cell (True = missing).
    # .sum() adds up the Trues (True = 1, False = 0) to count missing values.
    missing = df.isnull().sum()
    print("\nMissing Values:")
    for col, count in missing.items():
        print(f"  {col:30s} -> {count}")

    # --- Numeric statistics ---
    # select_dtypes(include="number") filters to only numeric columns.
    # This way we don't try to calculate the "average" of names or departments.
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        # Print a formatted header for the statistics table.
        # The :>12s means "right-align in a 12-character wide space".
        print("\nNumeric Column Statistics:")
        print(f"  {'Column':30s} {'Min':>12s} {'Max':>12s} {'Mean':>12s} {'Median':>12s}")
        print("  " + "-" * 80)

        for col in numeric_cols:
            # .min() = smallest value in the column
            # .max() = largest value in the column
            # .mean() = average (sum of all values / count of values)
            # .median() = the middle value when all values are sorted
            # Note: NaN values are automatically ignored by these functions.
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_median = df[col].median()

            # :12.2f means "12 characters wide, 2 decimal places, float format"
            print(f"  {col:30s} {col_min:12.2f} {col_max:12.2f} {col_mean:12.2f} {col_median:12.2f}")
    else:
        print("\nNo numeric columns found in the dataset.")

    print("=" * 60 + "\n")


# =============================================================================
# FUNCTION 3: filter_data
# =============================================================================
# Purpose: Filters the dataframe to only show rows where a specific column
#          matches a specific value.
#
# Example: filter_data(df, "Department", "Engineering")
#          This would return only the rows where Department is "Engineering".
#
# How it works:
#   1. First checks if the column name actually exists in the data.
#   2. If the column contains numbers, it converts the user's input to a number
#      and does an exact numeric comparison.
#   3. If the column contains text, it does a case-insensitive comparison
#      (so "engineering" matches "Engineering").
#
# What does df[df[column] == value] do?
#   - df[column] == value creates a True/False series (True for matching rows).
#   - df[...] with that True/False series returns only the True rows.
#   - This is called "boolean indexing" — a core pandas technique.
# =============================================================================
def filter_data(df, column, value):
    """Returns rows where the given column matches the given value."""

    # Check if the column exists. If not, print an error and return unchanged data.
    if column not in df.columns:
        print(f"\n[ERROR] Column '{column}' does not exist.\n")
        return df

    # Check if the column holds numeric data.
    # pd.api.types.is_numeric_dtype() returns True for int and float columns.
    if pd.api.types.is_numeric_dtype(df[column]):
        try:
            # The user types everything as a string, so we convert to float.
            # If they typed "abc" for a numeric column, this will fail.
            value = float(value)
        except ValueError:
            print("\n[ERROR] That column is numeric but the value you entered is not a number.\n")
            return df

        # Compare each value in the column to the target value.
        filtered = df[df[column] == value]
    else:
        # For text columns, we convert both sides to lowercase so the match
        # is case-insensitive ("engineering" matches "Engineering").
        # .astype(str) converts everything to a string first (handles NaN safely).
        filtered = df[df[column].astype(str).str.lower() == value.lower()]

    print(f"\n[OK] Filter returned {len(filtered)} row(s).\n")
    return filtered


# =============================================================================
# FUNCTION 4: sort_data
# =============================================================================
# Purpose: Sorts the dataframe by a column in ascending or descending order.
#
# What is ascending vs descending?
#   - Ascending (A to Z, 1 to 100): smallest/earliest first
#   - Descending (Z to A, 100 to 1): largest/latest first
#
# df.sort_values() is the pandas function that does the sorting.
# The "by" parameter tells it which column to sort by.
# The "ascending" parameter is True (A-Z) or False (Z-A).
# =============================================================================
def sort_data(df, column, ascending=True):
    """Returns the dataframe sorted by the specified column."""

    if column not in df.columns:
        print(f"\n[ERROR] Column '{column}' does not exist.\n")
        return df

    # sort_values creates a NEW sorted dataframe (doesn't change the original).
    sorted_df = df.sort_values(by=column, ascending=ascending)

    order = "ascending" if ascending else "descending"
    print(f"\n[OK] Data sorted by '{column}' ({order}).\n")
    return sorted_df


# =============================================================================
# FUNCTION 5: export_csv
# =============================================================================
# Purpose: Saves the current dataframe to a new CSV file.
#
# df.to_csv() writes the dataframe out as a CSV file.
# index=False means we don't save the row numbers (0, 1, 2, ...) as a column
# in the output file. Without this, you'd get an extra unnamed column.
#
# Why try/except? The user might try to save to a read-only location, or the
# path might be invalid. We catch those errors instead of crashing.
# =============================================================================
def export_csv(df, output_path):
    """Saves the dataframe to a new CSV file."""

    try:
        df.to_csv(output_path, index=False)
        print(f"\n[OK] Data exported successfully to '{output_path}'.\n")
    except PermissionError:
        # Happens when the file/folder is read-only or in use by another program.
        print(f"\n[ERROR] Permission denied: cannot write to '{output_path}'.\n")
    except Exception as e:
        print(f"\n[ERROR] Error exporting file: {e}\n")


# =============================================================================
# FUNCTION 6: show_menu
# =============================================================================
# Purpose: Simply prints the menu options. Separated into its own function so
#          the main loop stays clean and readable.
# =============================================================================
def show_menu():
    """Displays the main menu options."""
    print("-" * 40)
    print("  CSV Analyzer - Main Menu")
    print("-" * 40)
    print("  1. Show summary")
    print("  2. Filter data")
    print("  3. Sort data")
    print("  4. Export to CSV")
    print("  5. Exit")
    print("-" * 40)


# =============================================================================
# FUNCTION 7: main
# =============================================================================
# Purpose: The main entry point. This function:
#   1. Asks the user for a CSV file path
#   2. Loads the file
#   3. Shows a menu in a loop until the user picks "Exit"
#
# We use a "working copy" (working_df) so that when the user filters or sorts,
# those changes are applied to their working data, but the original data (df)
# stays untouched in case they need to start over.
#
# The while True loop runs forever until the user picks option 5 (Exit),
# which triggers "break" to exit the loop.
# =============================================================================
def main():
    """Main function that runs the CSV analyzer."""

    print("\n>> Welcome to the CSV Analyzer!\n")

    # input() pauses the program and waits for the user to type something.
    # .strip() removes any extra spaces or newlines from what they typed.
    filepath = input("Enter the path to your CSV file: ").strip()
    df = load_csv(filepath)

    # If load_csv returned None, that means the file couldn't be loaded.
    # So we just stop the program here.
    if df is None:
        return

    # .copy() makes a separate copy of the dataframe.
    # Changes to working_df won't affect df, and vice versa.
    working_df = df.copy()

    # This loop keeps showing the menu until the user picks Exit.
    while True:
        show_menu()
        choice = input("Pick an option (1-5): ").strip()

        if choice == "1":
            # Option 1: Show the full data summary
            summarize(working_df)

        elif choice == "2":
            # Option 2: Filter the data
            # First show which columns exist so the user knows what to type.
            print(f"\nAvailable columns: {', '.join(working_df.columns)}")
            col = input("Enter column name to filter by: ").strip()
            val = input("Enter value to match: ").strip()
            result = filter_data(working_df, col, val)

            if not result.empty:
                # .to_string(index=False) prints the dataframe as a nice table
                # without the row index numbers on the left side.
                print(result.to_string(index=False))

                # Ask if they want to keep working with only the filtered data.
                keep = input("\nApply this filter to the working data? (y/n): ").strip().lower()
                if keep == "y":
                    working_df = result
                    print("[OK] Working data updated with filter.\n")
            else:
                print("No rows matched your filter.\n")

        elif choice == "3":
            # Option 3: Sort the data
            print(f"\nAvailable columns: {', '.join(working_df.columns)}")
            col = input("Enter column name to sort by: ").strip()
            order = input("Sort ascending? (y/n): ").strip().lower()

            # If they type "n", ascending is False (descending).
            # Anything else (including "y") means ascending.
            ascending = order != "n"
            working_df = sort_data(working_df, col, ascending)

            # .head(10) shows only the first 10 rows so we don't flood the screen.
            print(working_df.head(10).to_string(index=False))
            print("  (showing first 10 rows)\n")

        elif choice == "4":
            # Option 4: Export current data to a new CSV file
            out_path = input("Enter output file path (e.g. output.csv): ").strip()
            export_csv(working_df, out_path)

        elif choice == "5":
            # Option 5: Exit the program
            print("\nGoodbye!\n")
            break  # "break" exits the while True loop, ending the program.

        else:
            # If they typed something other than 1-5
            print("\n[!] Invalid choice. Please enter a number from 1 to 5.\n")


# =============================================================================
# WHAT DOES THIS DO?
# =============================================================================
# This is a Python convention. It checks: "Is this file being run directly?"
#
# - If you run "python csv_analyzer_explained.py", then __name__ == "__main__"
#   is True, so main() gets called and the program starts.
#
# - If another script does "from csv_analyzer_explained import load_csv",
#   then __name__ would NOT be "__main__", so main() won't run automatically.
#   This lets other scripts use our functions without starting the menu.
# =============================================================================
if __name__ == "__main__":
    main()
