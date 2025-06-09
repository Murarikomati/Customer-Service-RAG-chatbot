import pyodbc
from tabulate import tabulate
import pandas as pd
def connect_to_database(server, database, username, password, encrypt=True, trust_cert=True, driver="ODBC Driver 17 for SQL Server"):
    """
    Connects to a SQL Server instance using SQL Authentication.
    
    Args:
        server (str): SQL Server address, e.g., 'DESKTOP-XXXX\\SQLEXPRESS'
        database (str): Database name to connect to
        username (str): SQL login username, e.g., 'sa'
        password (str): SQL login password
        encrypt (bool): Whether to use encryption
        trust_cert (bool): Whether to trust the server certificate
        driver (str): ODBC driver to use (default: 'ODBC Driver 17 for SQL Server')
        
    Returns:
        pyodbc.Connection or None
    """
    try:
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt={'yes' if encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if trust_cert else 'no'};"
        )
        conn = pyodbc.connect(conn_str)
        print(f"✅ Connected to database: {database} on {server}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None


# def get_database_schema(conn):
#     """
#     Prints CREATE TABLE statements for all user tables in the connected database.
#     """
#     try:
#         cursor = conn.cursor()

#         # Get all base tables
#         cursor.execute("""
#             SELECT TABLE_SCHEMA, TABLE_NAME
#             FROM INFORMATION_SCHEMA.TABLES
#             WHERE TABLE_TYPE = 'BASE TABLE';
#         """)
#         tables = cursor.fetchall()

#         for schema, table in tables:
#             print(f"\n📄 Table: {schema}.{table}")

#             # Get columns and metadata
#             cursor.execute(f"""
#                 SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
#                 FROM INFORMATION_SCHEMA.COLUMNS
#                 WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?;
#             """, schema, table)

#             columns = cursor.fetchall()

#             ddl = f"CREATE TABLE {schema}.{table} (\n"
#             col_defs = []
#             for col in columns:
#                 col_name, data_type, char_len, num_precision, num_scale = col
#                 if data_type in ("varchar", "nvarchar", "char", "nchar"):
#                     col_def = f"    [{col_name}] {data_type}({char_len})"
#                 elif data_type in ("decimal", "numeric"):
#                     col_def = f"    [{col_name}] {data_type}({num_precision},{num_scale})"
#                 else:
#                     col_def = f"    [{col_name}] {data_type}"
#                 col_defs.append(col_def)

#             ddl += ",\n".join(col_defs) + "\n);"
#             print(ddl)

#     except Exception as e:
#         print("❌ Failed to retrieve schema:", e)

# def get_database_schema_with_samples(conn, database=None):
#     """
#     Returns a dictionary with table names as keys, and values as:
#     - 'schema': MySQL-style CREATE TABLE statement
#     - 'sample_rows': up to 3 row dictionaries per table
#     """
#     schema_info = {}
#     try:
#         cursor = conn.cursor()

#         # Optionally switch to desired database
#         if database:
#             cursor.execute(f"USE [{database}]")

#         # Get all base tables
#         cursor.execute("""
#             SELECT TABLE_SCHEMA, TABLE_NAME
#             FROM INFORMATION_SCHEMA.TABLES
#             WHERE TABLE_TYPE = 'BASE TABLE'
#             ORDER BY TABLE_SCHEMA, TABLE_NAME;
#         """)
#         tables = cursor.fetchall()

#         for schema, table in tables:
#             full_table_name = f"{schema}.{table}"
#             print(f"\n📄 Processing table: {full_table_name}")

#             # Get column definitions
#             cursor.execute("""
#                 SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
#                        NUMERIC_PRECISION, NUMERIC_SCALE
#                 FROM INFORMATION_SCHEMA.COLUMNS
#                 WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
#                 ORDER BY ORDINAL_POSITION;
#             """, schema, table)
#             columns = cursor.fetchall()

#             ddl = f"CREATE TABLE {table} (\n"
#             col_defs = []

#             for col_name, data_type, char_len, num_precision, num_scale in columns:
#                 if data_type in ("varchar", "nvarchar", "char", "nchar"):
#                     col_def = f"    `{col_name}` {data_type.upper()}({char_len})"
#                 elif data_type in ("decimal", "numeric"):
#                     col_def = f"    `{col_name}` {data_type.upper()}({num_precision},{num_scale})"
#                 elif data_type in ("int", "bigint", "smallint", "tinyint"):
#                     col_def = f"    `{col_name}` {data_type.upper()}"
#                 elif data_type in ("datetime", "date", "time"):
#                     col_def = f"    `{col_name}` {data_type.upper()}"
#                 else:
#                     col_def = f"    `{col_name}` {data_type.upper()}"
#                 col_defs.append(col_def)

#             ddl += ",\n".join(col_defs) + \
#                    "\n) DEFAULT CHARSET=utf8mb4 ENGINE=InnoDB COLLATE=utf8mb4_0900_ai_ci;"

#             # Get sample rows
#             try:
#                 cursor.execute(f"SELECT TOP 3 * FROM [{schema}].[{table}]")
#                 rows = cursor.fetchall()
#                 col_names = [desc[0] for desc in cursor.description]
#                 sample_rows = [dict(zip(col_names, row)) for row in rows]
#             except Exception as fetch_err:
#                 sample_rows = []
#                 print(f"⚠️ Could not fetch rows from {full_table_name}: {fetch_err}")

#             schema_info[full_table_name] = {
#                 "schema": ddl,
#                 "sample_rows": sample_rows
#             }

#     except Exception as e:
#         print("❌ Failed to retrieve schema:", e)

#     return schema_info

def get_database_schema_with_samples(conn, database=None):
    """
    Returns a dictionary with fully qualified table names (schema.table) as keys, and values as:
    - 'schema': SQL Server-style CREATE TABLE statement
    - 'sample_rows': up to 3 row dictionaries per table
    If database is None, scans all databases.
    """
    schema_info = {}
    cursor = conn.cursor()

    try:
        # Get target databases
        if database:
            databases = [database]
        else:
            cursor.execute("""
                SELECT name 
                FROM sys.databases
                WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb');  -- Exclude system DBs
            """)
            databases = [row[0] for row in cursor.fetchall()]

        for db_name in databases:
            print(f"\n🔍 Scanning database: {db_name}")
            try:
                cursor.execute(f"USE [{db_name}]")

                cursor.execute("""
                    SELECT TABLE_SCHEMA, TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_SCHEMA, TABLE_NAME;
                """)
                tables = cursor.fetchall()

                for schema, table in tables:
                    full_table_name = f"{db_name}.{schema}.{table}"
                    print(f"📄 Processing table: {full_table_name}")

                    # Get column definitions
                    cursor.execute("""
                        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
                               NUMERIC_PRECISION, NUMERIC_SCALE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION;
                    """, (schema, table))
                    columns = cursor.fetchall()

                    ddl = f"CREATE TABLE {schema}.{table} (\n"
                    col_defs = []

                    for col_name, data_type, char_len, num_precision, num_scale in columns:
                        if data_type in ("varchar", "nvarchar", "char", "nchar"):
                            col_def = f"    [{col_name}] {data_type.upper()}({char_len})"
                        elif data_type in ("decimal", "numeric"):
                            col_def = f"    [{col_name}] {data_type.upper()}({num_precision},{num_scale})"
                        else:
                            col_def = f"    [{col_name}] {data_type.upper()}"
                        col_defs.append(col_def)

                    ddl += ",\n".join(col_defs) + "\n);"

                    # Fetch sample rows
                    try:
                        cursor.execute(f"SELECT TOP 3 * FROM [{schema}].[{table}]")
                        rows = cursor.fetchall()
                        col_names = [desc[0] for desc in cursor.description]
                        sample_rows = [dict(zip(col_names, row)) for row in rows]
                    except Exception as fetch_err:
                        sample_rows = []
                        print(f"⚠️ Could not fetch rows from {full_table_name}: {fetch_err}")

                    schema_info[full_table_name] = {
                        "schema": ddl,
                        "sample_rows": sample_rows
                    }

            except Exception as db_err:
                print(f"❌ Failed to process database {db_name}: {db_err}")

    except Exception as e:
        print("❌ Unexpected error:", e)

    return schema_info


def ExecuteQueryInTables(conn, cleaned_query):
    """
    Executes one or more SQL statements and prints result sets (if any) in tabular format.
    
    Args:
        conn: Active pyodbc connection
        cleaned_query: SQL script string with one or more queries separated by ';'
    """
    cursor = conn.cursor()

    # Split by semicolon but keep statements clean
    queries = [q.strip() for q in cleaned_query.split(";") if q.strip()]
    result_output = []

    for idx, query in enumerate(queries, 1):
        try:
            cursor.execute(query)

            # Try to fetch rows only if the query returns rows
            try:
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                table = tabulate(rows, headers=columns, tablefmt="grid")
                result_output.append(f"\n📄 Result {idx}:\n{table}")
            except pyodbc.ProgrammingError:
                # No result set (e.g., DDL or UPDATE/INSERT)
                affected = cursor.rowcount
                result_output.append(f"\n✅ Statement {idx} executed successfully. Rows affected: {affected}")
        except Exception as e:
            result_output.append(f"\n❌ Error in statement {idx}:\n{e}")

    return "\n".join(result_output)
from decimal import Decimal

def ExecuteQuery(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    cursor.close()

    # Convert Decimal to float in each row
    cleaned_rows = []
    for row in rows:
        cleaned_row = [float(val) if isinstance(val, Decimal) else val for val in row]
        cleaned_rows.append(cleaned_row)

    return pd.DataFrame(cleaned_rows, columns=columns)

# import pandas as pd

# def ExecuteQuery(conn, query):
#     cursor = conn.cursor()
#     cursor.execute(query)
#     columns = [column[0] for column in cursor.description]
#     rows = cursor.fetchall()
#     cursor.close()
#     return pd.DataFrame(rows, columns=columns)

server = "DESKTOP-EQGHQH9\\SQLEXPRESS"
database = "master"
username = 'sa'
password = 'ssmsMurari@157'

# # conn = connect_to_database(server, database, username, password)
conn = connect_to_database(
    server= server,
    database= database,
    username=username,
    password=password
)

# ExecuteQuery(query="SELECT name FROM sys.databases;")

# if conn:
#     schema_data = get_database_schema_with_samples(conn,"RetailDB_RealTime")
#     for table, info in schema_data.items():
#         print(f"\n🧱 {table} Schema:")
#         print(info["schema"])
#         print("🔍 Sample Rows:")
#         for row in info["sample_rows"]:
#             print(row)