import asyncio
import datasette
from datasette.app import connections
from datasette.inspect import inspect_hash
from datasette.utils import Results
from pathlib import Path
import sqlite3

from . import connectors


def patch_datasette():
    """
    Monkey patching for original Datasette
    """

    def inspect(self):
        " Inspect the database and return a dictionary of table metadata "
        if self._inspect:
            return self._inspect

        _inspect = {}
        files = self.files

        for filename in files:
            self.files = (filename,)
            path = Path(filename)
            name = path.stem
            if name in _inspect:
                raise Exception("Multiple files with the same stem %s" % name)
            try:
                _inspect[name] = self.original_inspect()[name]
            except sqlite3.DatabaseError:
                tables, views, dbtype = connectors.inspect(path)
                _inspect[name] = {
                    "hash": inspect_hash(path),
                    "file": str(path),
                    "dbtype": dbtype,
                    "tables": tables,
                    "views": views,
                }

        self.files = files
        self._inspect = _inspect
        return self._inspect

    datasette.app.Datasette.original_inspect = datasette.app.Datasette.inspect
    datasette.app.Datasette.inspect = inspect


    async def execute(self, db_name, sql, params=None, truncate=False, custom_time_limit=None, page_size=None):
        """Executes sql against db_name in a thread"""
        page_size = page_size or self.page_size

        def is_sqlite3_conn():
            conn = getattr(connections, db_name, None)
            if not conn:
                info = self.inspect()[db_name]
                return info.get('dbtype', 'sqlite3') == 'sqlite3'
            else:
                return isinstance(conn, sqlite3.Connection)

        def sql_operation_in_thread():
            conn = getattr(connections, db_name, None)
            if not conn:
                info = self.inspect()[db_name]
                conn = connectors.connect(info['file'], info['dbtype'])
                setattr(connections, db_name, conn)

            rows, truncated, description = conn.execute(
                sql,
                params or {},
                truncate=truncate,
                page_size=page_size,
                max_returned_rows=self.max_returned_rows,
            )
            return Results(rows, truncated, description)

        if is_sqlite3_conn():
            return await self.original_execute(db_name, sql, params=params, truncate=truncate, custom_time_limit=custom_time_limit, page_size=page_size)
        else:
            return await asyncio.get_event_loop().run_in_executor(
                self.executor, sql_operation_in_thread
            )

    datasette.app.Datasette.original_execute = datasette.app.Datasette.execute
    datasette.app.Datasette.execute = execute
