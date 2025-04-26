import pandas as pd 
import duckdb
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


table_name="ratings"

def create_table_from_csv(con, table_name, csv_path):
    query = f"""
    CREATE OR REPLACE TABLE {table_name} AS 
    SELECT * FROM read_csv_auto('{csv_path}')
    """
    con.execute(query)
    print(f" Table '{table_name}' créée à partir de {csv_path}")


def show_tables(con):
    tables = con.execute("SHOW TABLES").fetchdf()
    print("Tables dans la base :")
    print(tables)

def main():
    con = duckdb.connect(config.DB_PATH)
    create_table_from_csv(con, table_name, config.CSV_PATH)
    show_tables(con)
    con.close()

if __name__ == "__main__":
    main()
