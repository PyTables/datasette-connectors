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
