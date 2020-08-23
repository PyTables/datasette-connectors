import pkg_resources
import functools

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

    @staticmethod
    @for_each_connector
    def table_names(connector, path):
        return connector.table_names(path)

    @staticmethod
    @for_each_connector
    def hidden_table_names(connector, path):
        return connector.hidden_table_names(path)

    @staticmethod
    @for_each_connector
    def view_names(connector, path):
        return connector.view_names(path)

    @staticmethod
    @for_each_connector
    def table_columns(connector, path, table):
        return connector.table_columns(path, table)

    @staticmethod
    @for_each_connector
    def primary_keys(connector, path, table):
        return connector.primary_keys(path, table)

    @staticmethod
    @for_each_connector
    def fts_table(connector, path, table):
        return connector.fts_table(path, table)

    @staticmethod
    @for_each_connector
    def get_all_foreign_keys(connector, path):
        return connector.get_all_foreign_keys(path)

    @staticmethod
    @for_each_connector
    def table_counts(connector, path, *args, **kwargs):
        return connector.table_counts(path, *args, **kwargs)


class Connector:
    @staticmethod
    def table_names(path):
        return []

    @staticmethod
    def hidden_table_names(path):
        return []

    @staticmethod
    def view_names(path):
        return []

    @staticmethod
    def table_columns(path, table):
        return []

    @staticmethod
    def primary_keys(path, table):
        return []

    @staticmethod
    def fts_table(path, table):
        return None

    @staticmethod
    def get_all_foreign_keys(path):
        return {}

    @staticmethod
    def table_counts(path, *args, **kwargs):
        return {}
