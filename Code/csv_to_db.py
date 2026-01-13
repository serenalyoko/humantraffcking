import pandas as pd
import sqlite3
import os
import json


if __name__ == "__main__":
    path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/finalized_data.csv"
    db_path = os.path.splitext(path)[0] + ".db"
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(path)
    
    # Create a connection to the SQLite database
    # The .db file will be created if it doesn't exist
    conn = sqlite3.connect(db_path)
    
    # Use the to_sql method to write the DataFrame to a SQL table
    # 'data' will be the name of the table in the database
    # if_exists='replace' will drop the table first if it already exists
    # index=False will prevent pandas from writing the DataFrame index as a column
    df.to_sql('data', conn, if_exists='replace', index=False)
    
    # Close the database connection
    conn.close()
    
    print(f"Successfully converted {os.path.basename(path)} to {os.path.basename(db_path)}")