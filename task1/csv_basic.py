import pandas as pd


def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        print(f"\nLoaded '{filepath}' — {df.shape[0]} rows, {df.shape[1]} columns.\n")
        return df
    except FileNotFoundError:
        print(f"\nError: File '{filepath}' not found.\n")
        return None
    except Exception as e:
        print(f"\nError: {e}\n")
        return None


def summarize(df):
    print("=" * 50)
    print("  DATA SUMMARY")
    print("=" * 50)

    print(f"\nRows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Column Names: {', '.join(df.columns)}")

    print("\nData Types:")
    for col in df.columns:
        print(f"  {col} -> {df[col].dtype}")

    print("\nMissing Values:")
    for col, count in df.isnull().sum().items():
        print(f"  {col} -> {count}")

    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        print("\nNumeric Stats:")
        for col in numeric_cols:
            print(f"\n  {col}:")
            print(f"    Min:    {df[col].min():.2f}")
            print(f"    Max:    {df[col].max():.2f}")
            print(f"    Mean:   {df[col].mean():.2f}")
            print(f"    Median: {df[col].median():.2f}")

    print("\n" + "=" * 50)


def main():
    filepath = input("Enter CSV file path: ").strip()
    df = load_csv(filepath)
    if df is not None:
        summarize(df)


if __name__ == "__main__":
    main()
