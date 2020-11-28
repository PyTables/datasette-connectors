import pkg_resources
from .connection import Connection


db_connectors = {}


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


class Connector:
    connector_type = None
    connection_class = Connection

    @classmethod
    def connect(cls, path):
        return cls.connection_class(path, cls)

    def __init__(self, conn):
        self.conn = conn

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
