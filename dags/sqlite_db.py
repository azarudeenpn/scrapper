"""
SqliteDB class handles sqlite operations. This is a wrapper around sqlite3 standard module from python.
"""
import logging
import sqlite3


class SqliteDB:
    def __init__(self, database_path: str):
        self.database = database_path
        self.create_table_if_not_exists()

    def get_connection(self):
        """
        get_connection method returns a connection object.
        :param: database path
        :return: sqlite.connection() object
        :raise: exception if path is incorrect or other runtime error occurs
        """
        try:
            conn = sqlite3.connect(self.database)
            return conn
        except Exception as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise e

    def insert_update_delete_data(self, sql: str, data: tuple):
        """
        helper method to insert/update/delete data. This method is wraps around cur.execute() from sqlite3.
        for reference: https://docs.python.org/3/library/sqlite3.html#sqlite3-tutorial
        :param sql: sql statement with appropriate placeholders. example: INSERT INTO TABLE(name,email) VALUES(?,?)
        :param data: data to be replaced in placeholders given in first parameter
        :return: True if success/ False if failed.
        """
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(sql, data)
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Data insert/update/delete failed: {str(e)}")
            conn.rollback()
            return False

    def query(self, sql: str, data: str = None):
        """
        To query data from database.
        :param sql: select query. example: SELECT * FROM TABLE WHERE ID = ?
        :param data: data to replace placeholders. If no placeholders are there, data can be None.
        :return: Rows, This row object converted into list of dicts in address_api.py
        """
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row  # to get data as list of dict
            cur = conn.cursor()
            if data:
                cur.execute(sql, data)
            else:
                cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Data query failed: {str(e)}")
            return False

    def create_table_if_not_exists(self):
        """
        To create tables in db if not exists.
        """
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS category(id INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT, categories TEXT)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT,brand TEXT, name TEXT, price TEXT, category TEXT, url TEXT)")
            conn.commit()
        except Exception as e:
            logging.error(str(e))
            pass
