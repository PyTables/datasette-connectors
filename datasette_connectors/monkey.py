import threading
import sqlite3
import datasette.views.base
from datasette.database import Database

from .connectors import ConnectorList

connections = threading.local()


def patch_datasette():
    """
    Monkey patching for original Datasette
    """

    async def table_names(self):
        try:
            return await self.original_table_names()
        except sqlite3.DatabaseError:
            return ConnectorList.table_names(self.path)

    Database.original_table_names = Database.table_names
    Database.table_names = table_names


    async def hidden_table_names(self):
        try:
            return await self.original_hidden_table_names()
        except sqlite3.DatabaseError:
            return ConnectorList.hidden_table_names(self.path)

    Database.original_hidden_table_names = Database.hidden_table_names
    Database.hidden_table_names = hidden_table_names


    async def view_names(self):
        try:
            return await self.original_view_names()
        except sqlite3.DatabaseError:
            return ConnectorList.view_names(self.path)

    Database.original_view_names = Database.view_names
    Database.view_names = view_names


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


    async def get_all_foreign_keys(self):
        try:
            return await self.original_get_all_foreign_keys()
        except sqlite3.DatabaseError:
            return ConnectorList.get_all_foreign_keys(self.path)

    Database.original_get_all_foreign_keys = Database.get_all_foreign_keys
    Database.get_all_foreign_keys = get_all_foreign_keys


    async def table_counts(self, *args, **kwargs):
        counts = await self.original_table_counts(**kwargs)
        # If all tables has None as counts, an error had ocurred
        if len(list(filter(lambda table_count: table_count is not None, counts.values()))) == 0:
            return ConnectorList.table_counts(self.path, *args, **kwargs)

    Database.original_table_counts = Database.table_counts
    Database.table_counts = table_counts
