import pandas as pd
from sqlalchemy import create_engine
from Spider.keys import Credentials


class DataConverter:
    def __init__(self, csv_path, credentials=None, host=None, db_name=None, table_name=None):
        self.df = pd.read_csv(csv_path)
        if credentials is None:
            self.credentials = Credentials()
        else:
            self.credentials = credentials
        if host is None:
            self.host = 'localhost'
        else:
            self.host = host
        if db_name is None:
            self.db_name = 'spider_db'
        else:
            self.db_name = db_name
        if table_name is None:
            self.table_name = 'spider_table'
        else:
            self.table_name = table_name

    def remove_duplicates(self):
        self.df.drop_duplicates(inplace=True)

    def remove_na(self):
        self.df.dropna(inplace=True)

    def insert_to_db(self, table_name):
        # Create the database engine
        engine = create_engine(f"mysql+mysqlconnector://{self.credentials.username}:{self.credentials.password}@{self.host}/{self.db_name}")

        # Insert data into the database, append to existing table
        self.df.to_sql(self.table_name, engine, if_exists='append', index=False)


if __name__ == "__main__":
    converter = DataConverter('spider_memory.csv')
    converter.remove_duplicates()
    converter.remove_na()
    converter.insert_to_db('spider_table')