# Week 1

## Task 1: CSV Analyzer Scripts

Two Python scripts that load and analyze CSV files using pandas.

---

### csv_basic.py - Simple CSV Analyzer

A lightweight script that loads a CSV file and prints a summary of the data.

**Features:**
- Loads any CSV file by entering the file path
- Displays the number of rows and columns
- Lists all column names and their data types
- Shows missing value count per column
- Prints min, max, mean, and median for all numeric columns

**How to run:**
```
python csv_basic.py
```

---

### csv_analyzer.py - Full CSV Analyzer

An interactive menu-driven script with full data analysis, filtering, sorting, and export functionality.

**Features:**
- Loads any CSV file by entering the file path
- Full data summary (rows, columns, data types, missing values, numeric stats)
- Filter data by any column, supporting both text and numeric columns
- Sort data by any column in ascending or descending order
- Export the current working data to a new CSV file
- Changes (filters/sorts) apply to a working copy so the original data is preserved
- Interactive menu loop that stays open until you choose to exit

**How to run:**
```
python csv_analyzer.py
```

**Menu options:**
```
1. Show summary
2. Filter data
3. Sort data
4. Export to CSV
5. Exit
```

---

### Sample Data

A sample CSV file tgat i used is included in `task1/data/sample_data.csv` to test both scripts.

---


