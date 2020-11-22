import re
import sqlite3

from .row import Row


class OperationalError(Exception):
    pass


class Cursor:
    class QueryNotSupported(Exception):
        pass

    def __init__(self, conn):
        self.conn = conn
        self.connector = conn.connector_class(conn)
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
            match = re.search(r'PRAGMA table_info\(\[?\"?([\d\w\/%]*)\"?\]?\)', sql)
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
            if self.connector.table_exists(params['n']):
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
