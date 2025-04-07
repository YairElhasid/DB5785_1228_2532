import pandas as pd
import os
from sqlalchemy import create_engine

def csv_to_database(folder_path, db_connection_string):
    engine = create_engine(db_connection_string)

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)

            try:
                df = pd.read_csv(file_path)
                table_name = os.path.splitext(filename)[0]

                df.to_sql(table_name, engine, if_exists='replace', index=False)

                print(f"Successfully imported {filename} to table {table_name}")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    username = input("Enter database username: ")
    password = input("Enter database password: ")
    db_name = input("Enter database name: ")
    folder_path = input("Enter path to CSV folder: ")

    db_string = f"postgresql://{username}:{password}@localhost:5432/{db_name}"

    csv_to_database(folder_path, db_string)