import datasette_connectors as dc


class DummyConnector(dc.Connector):
    connector_type = 'dummy'

    def table_names(self):
        return ['table1', 'table2']

    def hidden_table_names(self):
        return []

    def detect_spatialite(self):
        return False

    def view_names(self):
        return []

    def table_count(self, table_name):
        return 2

    def table_info(self, table_name):
        return [
            {
                'idx': 0,
                'name': 'c1',
                'primary_key': False,
            },
            {
                'idx': 0,
                'name': 'c2',
                'primary_key': False,
            },
            {
                'idx': 0,
                'name': 'c3',
                'primary_key': False,
            },
        ]

    def detect_fts(self, table_name):
        return False

    def foreign_keys(self, table_name):
        return []

    def table_exists(self, table_name):
        return table_name in ['table1', 'table2']

    def table_definition(self, table_type, table_name):
        return 'CREATE TABLE ' + table_name + ' (c1, c2, c3)'

    def indices_definition(self, table_name):
        return []

    def execute(
        self,
        sql,
        params=None,
        truncate=False,
        custom_time_limit=None,
        page_size=None,
        log_sql_errors=True,
    ):
        results = []
        truncated = False
        description = ()

        if sql == 'select c1 from table1':
            results = [
                {'c1': 10},
                {'c1': 20},
            ]
            description = (('c1',),)
        elif sql == 'select c1, c2, c3 from table2 limit 51':
            results = [
                {'c1': 100, 'c2': 120, 'c3': 130},
                {'c1': 200, 'c2': 220, 'c3': 230},
            ]
            description = (('c1',), ('c2',), ('c3',))
        elif sql == "select * from (select c1, c2, c3 from table2 ) limit 0":
            pass
        elif sql == "select c1, count(*) as n from ( select c1, c2, c3 from table2 ) where c1 is not null group by c1 limit 31":
            results = [
                {'c1': 100, 'n': 1},
                {'c1': 200, 'n': 1},
            ]
            description = (('c1',), ('n',))
        elif sql == "select c2, count(*) as n from ( select c1, c2, c3 from table2 ) where c2 is not null group by c2 limit 31":
            results = [
                {'c2': 120, 'n': 1},
                {'c2': 220, 'n': 1},
            ]
            description = (('c2',), ('n',))
        elif sql == "select c3, count(*) as n from ( select c1, c2, c3 from table2 ) where c3 is not null group by c3 limit 31":
            results = [
                {'c3': 130, 'n': 1},
                {'c3': 230, 'n': 1},
            ]
            description = (('c3',), ('n',))
        elif sql == 'select date(c1) from ( select c1, c2, c3 from table2 ) where c1 glob "????-??-*" limit 100;':
            pass
        elif sql == "select c1, c2, c3 from blah limit 51":
            raise dc.OperationalError("no such table: blah")
        else:
            raise Exception("Unexpected query:", sql)

        return results, truncated, description
