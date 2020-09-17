import asyncio
import threading
import sqlite3

import datasette.views.base
from datasette.tracer import trace
from datasette.database import Database
from datasette.database import Results

from .connectors import ConnectorList

connections = threading.local()


def patch_datasette():
    """
    Monkey patching for original Datasette
    """

    async def table_columns(self, table):
        try:
            return await self.original_table_columns(table)
        except sqlite3.DatabaseError:
            return ConnectorList.table_columns(self.path, table)

    Database.original_table_columns = Database.table_columns
    Database.table_columns = table_columns


    async def primary_keys(self, table):
        try:
            return await self.original_primary_keys(table)
        except sqlite3.DatabaseError:
            return ConnectorList.primary_keys(self.path, table)

    Database.original_primary_keys = Database.primary_keys
    Database.primary_keys = primary_keys


    async def fts_table(self, table):
        try:
            return await self.original_fts_table(table)
        except sqlite3.DatabaseError:
            return ConnectorList.fts_table(self.path, table)

    Database.original_fts_table = Database.fts_table
    Database.fts_table = fts_table


    def connect(self, write=False):
        try:
            # Check if it's a sqlite database
            conn = self.original_connect(write=write)
            conn.execute("select name from sqlite_master where type='table'")
            return conn
        except sqlite3.DatabaseError:
            conn = ConnectorList.connect(self.path)
            return conn

    Database.original_connect = Database.connect
    Database.connect = connect


    async def execute_fn(self, fn):
        def in_thread():
            conn = getattr(connections, self.name, None)
            if not conn:
                conn = self.connect()
                if isinstance(conn, sqlite3.Connection):
                    self.ds._prepare_connection(conn, self.name)
                setattr(connections, self.name, conn)
            return fn(conn)

        return await asyncio.get_event_loop().run_in_executor(
            self.ds.executor, in_thread
        )

    Database.original_execute_fn = Database.execute_fn
    Database.execute_fn = execute_fn
