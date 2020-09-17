import pkg_resources
import functools
import re
import sqlite3

from .row import Row


db_connectors = {}

def for_each_connector(func):
    @functools.wraps(func)
    def wrapper_for_each_connector(*args, **kwargs):
        for connector in db_connectors.values():
            try:
                return func(connector, *args, **kwargs)
            except:
                pass
        else:
            raise Exception("No database connector found!!")
    return wrapper_for_each_connector


class ConnectorList:
    @staticmethod
    def load():
        for entry_point in pkg_resources.iter_entry_points('datasette.connectors'):
            db_connectors[entry_point.name] = entry_point.load()

    @staticmethod
    def add_connector(name, connector):
        db_connectors[name] = connector

    class DatabaseNotSupported(Exception):
        pass

    @staticmethod
    def connect(path):
        for connector in db_connectors.values():
            try:
                return connector.connect(path)
            except:
                pass
        else:
            raise ConnectorList.DatabaseNotSupported


class Connection:
    def __init__(self, path, connector):
        self.path = path
        self.connector = connector

    def execute(self, *args, **kwargs):
        cursor = Cursor(self)
        cursor.execute(*args, **kwargs)
        return cursor

    def cursor(self):
        return Cursor(self)

    def set_progress_handler(self, handler, n):
        pass


class OperationalError(Exception):
    pass


class Cursor:
    class QueryNotSupported(Exception):
        pass

    def __init__(self, conn):
        self.conn = conn
        self.connector = conn.connector
        self.rows = []
        self.description = ()

    def execute(
        self,
        sql,
        params=None,
        truncate=False,
        custom_time_limit=None,
        page_size=None,
        log_sql_errors=True,
    ):
        if params is None:
            params = {}
        results = []
        truncated = False
        description = ()

        # Normalize sql
        sql = sql.strip()
        sql = ' '.join(sql.split())

        if sql == "select name from sqlite_master where type='table'" or \
           sql == "select name from sqlite_master where type=\"table\"":
            results = [{'name': name} for name in self.connector.table_names()]
        elif sql == "select name from sqlite_master where rootpage = 0 and sql like '%VIRTUAL TABLE%USING FTS%'":
            results = [{'name': name} for name in self.connector.hidden_table_names()]
        elif sql == 'select 1 from sqlite_master where tbl_name = "geometry_columns"':
            if self.connector.detect_spatialite():
                results = [{'1': '1'}]
        elif sql == "select name from sqlite_master where type='view'":
            results = [{'name': name} for name in self.connector.view_names()]
        elif sql.startswith("select count(*) from ["):
            match = re.search(r'select count\(\*\) from \[(.*)\]', sql)
            results = [{'count(*)': self.connector.table_count(match.group(1))}]
        elif sql.startswith("select count(*) from "):
            match = re.search(r'select count\(\*\) from (.*)', sql)
            results = [{'count(*)': self.connector.table_count(match.group(1))}]
        elif sql.startswith("PRAGMA table_info("):
            match = re.search(r'PRAGMA table_info\((.*)\)', sql)
            results = self.connector.table_info(match.group(1))
        elif sql.startswith("select name from sqlite_master where rootpage = 0 and ( sql like \'%VIRTUAL TABLE%USING FTS%content="):
            match = re.search(r'select name from sqlite_master where rootpage = 0 and \( sql like \'%VIRTUAL TABLE%USING FTS%content="(.*)"', sql)
            if self.connector.detect_fts(match.group(1)):
                results = [{'name': match.group(1)}]
        elif sql.startswith("PRAGMA foreign_key_list(["):
            match = re.search(r'PRAGMA foreign_key_list\(\[(.*)\]\)', sql)
            results = self.connector.foreign_keys(match.group(1))
        elif sql == "select 1 from sqlite_master where type='table' and name=?":
            if self.connector.table_exists(params[0]):
                results = [{'1': '1'}]
        elif sql == "select sql from sqlite_master where name = :n and type=:t":
            results = [{'sql': self.connector.table_definition(params['t'], params['n'])}]
        elif sql == "select sql from sqlite_master where tbl_name = :n and type='index' and sql is not null":
            results = [{'sql': sql} for sql in self.connector.indices_definition(params['n'])]
        else:
            try:
                results, truncated, description = \
                    self.connector.execute(
                        sql,
                        params=params,
                        truncate=truncate,
                        custom_time_limit=custom_time_limit,
                        page_size=page_size,
                        log_sql_errors=log_sql_errors,
                    )
            except OperationalError as ex:
                raise sqlite3.OperationalError(*ex.args)

        self.rows = [Row(result) for result in results]
        self.description = description

    def fetchall(self):
        return self.rows

    def fetchmany(self, max):
        return self.rows[:max]

    def __getitem__(self, index):
        return self.rows[index]


class Connector:
    connector_type = None
    connection_class = Connection

    def connect(self, path):
        return self.connection_class(path, self)

    def table_names(self):
        """
        Return a list of table names
        """
        raise NotImplementedError

    def hidden_table_names(self):
        raise NotImplementedError

    def detect_spatialite(self):
        """
        Return boolean indicating if geometry_columns exists
        """
        raise NotImplementedError

    def view_names(self):
        """
        Return a list of view names
        """
        raise NotImplementedError

    def table_count(self, table_name):
        """
        Return an integer with the rows count of the table
        """
        raise NotImplementedError

    def table_info(self, table_name):
        """
        Return a list of dictionaries with columns description, with format:
        [
            {
                'idx': 0,
                'name': 'column1',
                'primary_key': False,
            },
            ...
        ]
        """
        raise NotImplementedError

    def detect_fts(self, table_name):
        """
        Return boolean indicating if table has a corresponding FTS virtual table
        """
        raise NotImplementedError

    def foreign_keys(self, table_name):
        """
        Return a list of dictionaries with foreign keys description
        id, seq, table_name, from_, to_, on_update, on_delete, match
        """
        raise NotImplementedError

    def table_exists(self, table_name):
        """
        Return boolean indicating if table exists in the database
        """
        raise NotImplementedError

    def table_definition(self, table_type, table_name):
        """
        Return string with a 'CREATE TABLE' sql definition
        """
        raise NotImplementedError

    def indices_definition(self, table_name):
        """
        Return a list of strings with 'CREATE INDEX' sql definitions
        """
        raise NotImplementedError

    def execute(
        self,
        sql,
        params=None,
        truncate=False,
        custom_time_limit=None,
        page_size=None,
        log_sql_errors=True,
    ):
        raise NotImplementedError
