import pandas as pd


def load_csv(filepath):
    """Loads a CSV file into a DataFrame and returns it."""
    try:
        df = pd.read_csv(filepath)
        print(f"\n[OK] Successfully loaded '{filepath}' ({df.shape[0]} rows, {df.shape[1]} columns).\n")
        return df
    except FileNotFoundError:
        print(f"\n[ERROR] File '{filepath}' was not found. Please check the path and try again.\n")
        return None
    except pd.errors.EmptyDataError:
        print(f"\n[ERROR] File '{filepath}' is empty.\n")
        return None
    except Exception as e:
        print(f"\n[ERROR] Error reading file: {e}\n")
        return None


def summarize(df):
    """Prints a full summary of the dataframe including shape, types, missing values, and numeric stats."""
    print("\n" + "=" * 60)
    print("                   DATA SUMMARY")
    print("=" * 60)

    rows, cols = df.shape
    print(f"\nRows    : {rows}")
    print(f"Columns : {cols}")

    print(f"\nColumn Names:\n  {', '.join(df.columns)}")

    print("\nData Types:")
    for col in df.columns:
        print(f"  {col:30s} -> {df[col].dtype}")

    missing = df.isnull().sum()
    print("\nMissing Values:")
    for col, count in missing.items():
        print(f"  {col:30s} -> {count}")

    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        print("\nNumeric Column Statistics:")
        print(f"  {'Column':30s} {'Min':>12s} {'Max':>12s} {'Mean':>12s} {'Median':>12s}")
        print("  " + "-" * 80)
        for col in numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_median = df[col].median()
            print(f"  {col:30s} {col_min:12.2f} {col_max:12.2f} {col_mean:12.2f} {col_median:12.2f}")
    else:
        print("\nNo numeric columns found in the dataset.")

    print("=" * 60 + "\n")


def filter_data(df, column, value):
    """Returns rows where the given column matches the given value."""
    if column not in df.columns:
        print(f"\n[ERROR] Column '{column}' does not exist.\n")
        return df

    if pd.api.types.is_numeric_dtype(df[column]):
        try:
            value = float(value)
        except ValueError:
            print("\n[ERROR] That column is numeric but the value you entered is not a number.\n")
            return df
        filtered = df[df[column] == value]
    else:
        filtered = df[df[column].astype(str).str.lower() == value.lower()]

    print(f"\n[OK] Filter returned {len(filtered)} row(s).\n")
    return filtered


def sort_data(df, column, ascending=True):
    """Returns the dataframe sorted by the specified column."""
    if column not in df.columns:
        print(f"\n[ERROR] Column '{column}' does not exist.\n")
        return df

    sorted_df = df.sort_values(by=column, ascending=ascending)
    order = "ascending" if ascending else "descending"
    print(f"\n[OK] Data sorted by '{column}' ({order}).\n")
    return sorted_df


def export_csv(df, output_path):
    """Saves the dataframe to a new CSV file."""
    try:
        df.to_csv(output_path, index=False)
        print(f"\n[OK] Data exported successfully to '{output_path}'.\n")
    except PermissionError:
        print(f"\n[ERROR] Permission denied: cannot write to '{output_path}'.\n")
    except Exception as e:
        print(f"\n[ERROR] Error exporting file: {e}\n")


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


def main():
    """Main function that runs the CSV analyzer."""
    print("\n>> Welcome to the CSV Analyzer!\n")

    filepath = input("Enter the path to your CSV file: ").strip()
    df = load_csv(filepath)

    if df is None:
        return

    working_df = df.copy()

    while True:
        show_menu()
        choice = input("Pick an option (1-5): ").strip()

        if choice == "1":
            summarize(working_df)

        elif choice == "2":
            print(f"\nAvailable columns: {', '.join(working_df.columns)}")
            col = input("Enter column name to filter by: ").strip()
            val = input("Enter value to match: ").strip()
            result = filter_data(working_df, col, val)

            if not result.empty:
                print(result.to_string(index=False))
                keep = input("\nApply this filter to the working data? (y/n): ").strip().lower()
                if keep == "y":
                    working_df = result
                    print("[OK] Working data updated with filter.\n")
            else:
                print("No rows matched your filter.\n")

        elif choice == "3":
            print(f"\nAvailable columns: {', '.join(working_df.columns)}")
            col = input("Enter column name to sort by: ").strip()
            order = input("Sort ascending? (y/n): ").strip().lower()
            ascending = order != "n"
            working_df = sort_data(working_df, col, ascending)
            print(working_df.head(10).to_string(index=False))
            print("  (showing first 10 rows)\n")

        elif choice == "4":
            out_path = input("Enter output file path (e.g. output.csv): ").strip()
            export_csv(working_df, out_path)

        elif choice == "5":
            print("\nGoodbye!\n")
            break

        else:
            print("\n[!] Invalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()
