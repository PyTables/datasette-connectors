from datasette_connectors.row import Row
from datasette_connectors.connectors import Connector


class DummyConnector(Connector):
    _connector_type = 'dummy'

    @staticmethod
    def table_names(path):
        return ['table1', 'table2']

    @staticmethod
    def table_columns(path, table):
        return ['c1', 'c2', 'c3']

    @staticmethod
    def get_all_foreign_keys(path):
        return {
            'table1': {'incoming': [], 'outgoing': []},
            'table2': {'incoming': [], 'outgoing': []},
        }

    @staticmethod
    def table_counts(path, *args, **kwargs):
        return {
            'table1': 2,
            'table2': 2,
        }


def inspect(path):
    tables = {}
    views = []

    for table in ['table1', 'table2']:
        tables[table] = {
            'name': table,
            'columns': ['c1', 'c2', 'c3'],
            'primary_keys': [],
            'count': 2,
            'label_column': None,
            'hidden': False,
            'fts_table': None,
            'foreign_keys': {'incoming': [], 'outgoing': []},
        }

    return tables, views, _connector_type


class Connection:
    def __init__(self, path):
        self.path = path

    def execute(self, sql, params=None, truncate=False, page_size=None, max_returned_rows=None):
        sql = sql.strip()

        rows = []
        truncated = False
        description = []

        if sql == 'select c1 from table1':
            rows = [
                Row({'c1': 10}),
                Row({'c1': 20})
            ]
            description = (('c1',),)
        elif sql == 'select rowid, * from table2 order by rowid limit 51':
            rows = [
                Row({'rowid': 1, 'c1': 100, 'c2': 120, 'c3': 130}),
                Row({'rowid': 2, 'c1': 200, 'c2': 220, 'c3': 230})
            ]
            description = (('rowid',), ('c1',), ('c2',), ('c3',))
        elif sql == 'select count(*) from table2':
            rows = [Row({'count(*)': 2})]
            description = (('count(*)',),)
        elif sql == """select distinct rowid from table2 
                        where rowid is not null
                        limit 31""":
            rows = [
                Row({'rowid': 1}),
                Row({'rowid': 2})
            ]
            description = (('rowid',),)
        elif sql == """select distinct c1 from table2 
                        where c1 is not null
                        limit 31""":
            rows = [
                Row({'c1': 100}),
                Row({'c1': 200})
            ]
            description = (('c1',),)
        elif sql == """select distinct c2 from table2 
                        where c2 is not null
                        limit 31""":
            rows = [
                Row({'c2': 120}),
                Row({'c2': 220})
            ]
            description = (('c2',),)
        elif sql == """select distinct c3 from table2 
                        where c3 is not null
                        limit 31""":
            rows = [
                Row({'c3': 130}),
                Row({'c3': 230})
            ]
            description = (('c3',),)
        elif sql == 'select sql from sqlite_master where name = :n and type=:t':
            if params['t'] != 'view':
                rows = [Row({'sql': 'CREATE TABLE ' + params['n'] + ' (c1, c2, c3)'})]
                description = (('sql',),)
        else:
            raise Exception("Unexpected query: %s" % sql)

        return rows, truncated, description
