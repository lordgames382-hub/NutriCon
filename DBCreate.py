import sqlite3
import os
import re

def new_db(db_name: str):
    """
    Creates a new SQLite database with the given name.
    If it already exists, it will just connect to it.
    
    :param db_name: Name of the database file (without .db extension)
    """
    
    # Ensure .db extension
    if not db_name.endswith(".db"):
        db_name = db_name + ".db"
    
    # Create database file
    conn = sqlite3.connect(db_name)
    
    # Optional: verify creation
    print(f"Database '{db_name}' created successfully at {os.path.abspath(db_name)}")

    conn.close()

def new_table(db_name: str, table_name: str, stop_word: str = "done"):
    """
    Creates a new SQLite table by prompting user for column definitions.
    Validates definitions before creating actual table.
    """

    if not db_name.endswith(".db"):
        db_name += ".db"

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print(f"\nCreating table '{table_name}'")
    print(f"Enter column definitions. Type '{stop_word}' when finished.\n")

    print("Examples:")
    print("  id INTEGER PRIMARY KEY AUTOINCREMENT")
    print("  name TEXT NOT NULL")
    print("  email TEXT UNIQUE")
    print("  department_id INTEGER")
    print("  FOREIGN KEY(department_id) REFERENCES departments(id)")
    print()

    columns = []

    # Simple regex for basic column validation
    column_pattern = re.compile(
        r"^(FOREIGN KEY\s*\(.+\)\s*REFERENCES\s+\w+\s*\(.+\)|\w+\s+\w+.*)$",
        re.IGNORECASE
    )

    while True:
        user_input = input("Enter column definition: ").strip()

        if user_input.lower() == stop_word.lower():
            break

        if not user_input:
            print("Error: Empty definition.")
            continue

        # Basic format validation
        if not column_pattern.match(user_input):
            print("Error: Invalid column definition format.")
            print("Expected formats like:")
            print("  column_name TYPE CONSTRAINTS")
            print("  FOREIGN KEY(column) REFERENCES table(column)")
            continue

        columns.append(user_input)

    if not columns:
        print("No columns entered. Table not created.")
        conn.close()
        return

    columns_sql = ",\n    ".join(columns)

    # Test validation using temporary table
    test_table = f"__test__{table_name}"

    test_sql = f"""
    CREATE TABLE {test_table} (
        {columns_sql}
    );
    """

    try:
        cursor.execute(test_sql)
        cursor.execute(f"DROP TABLE {test_table}")
    except sqlite3.Error as e:
        print("\nValidation Error:", e)
        print("Table was NOT created.")
        conn.close()
        return

    # Create real table
    real_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_sql}
    );
    """

    try:
        cursor.execute(real_sql)
        conn.commit()
        print(f"\nTable '{table_name}' created successfully.")

    except sqlite3.Error as e:
        print("Error creating table:", e)

    finally:
        conn.close()
    
def add_data(db_name: str, data_tuple: tuple):
    if not db_name.endswith(".db"):
        db_name += ".db"

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    table_name = input("Enter table name: ").strip()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()

    if not columns_info:
        print("Table does not exist.")
        return

    # Skip auto increment primary key columns
    insert_columns = [col[1] for col in columns_info if col[5] == 0]

    if len(data_tuple) != len(insert_columns):
        print(f"Expected {len(insert_columns)} values, got {len(data_tuple)}")
        return

    placeholders = ", ".join(["?"] * len(insert_columns))
    column_names = ", ".join(insert_columns)

    cursor.execute(
        f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
        data_tuple
    )

    conn.commit()
    conn.close()

    print("Data inserted successfully.")

def add_data_list(db_name: str, table_name: str, data_list: list):
    """
    Inserts multiple tuples into a SQLite table in alphabetical order.
    Automatically ignores AUTOINCREMENT primary key columns.

    :param db_name: Database name
    :param table_name: Table name
    :param data_list: List of tuples containing row data
    """

    if not db_name.endswith(".db"):
        db_name += ".db"

    if not data_list:
        print("Error: No data provided.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get table column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_info = cursor.fetchall()

        if not table_info:
            print(f"Error: Table '{table_name}' does not exist.")
            return

        # Exclude AUTOINCREMENT primary key columns
        # In SQLite, AUTOINCREMENT must be INTEGER PRIMARY KEY
        insertable_columns = [
            col for col in table_info
            if not (col[5] == 1 and col[2].upper() == "INTEGER")
        ]

        column_names = [col[1] for col in insertable_columns]
        column_count = len(column_names)

        # Validate tuple lengths
        for row in data_list:
            if len(row) != column_count:
                print(f"Error: Tuple {row} does not match required column count ({column_count}).")
                return

        # Sort alphabetically across full tuple
        sorted_data = sorted(
            data_list,
            key=lambda x: tuple(str(v).lower() for v in x)
        )

        placeholders = ", ".join(["?"] * column_count)
        columns_sql = ", ".join(column_names)

        cursor.executemany(
            f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})",
            sorted_data
        )

        conn.commit()

        print(f"{len(sorted_data)} rows inserted into '{table_name}' successfully.")

    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        conn.close()
            
    
    
