# How to make connectors for other data sources?

With Datasette-Connectors you can use [Datasette](https://github.com/simonw/datasette) for publishing data in your own format, not only SQLite, to the Internet with a JSON API. For this, you have to make connectors using the interface that is described here.

## Starting from scratch

For making a Datasette connector for your favorite database files, you need to inherit from `datasette_connectors.Connector`. Then, you can specify your connector type in the class property `connector_type` and, very important, you should set `connection_class` property with a class that inherits from `datasette_connectors.Connection` and implements a method for opening your database files.

For example, in [Datasette-PyTables](https://github.com/PyTables/datasette-pytables) the next class definition is used:

    import tables
    import datasette_connectors as dc

    class PyTablesConnection(dc.Connection):
        def __init__(self, path, connector):
            super().__init__(path, connector)
            self.h5file = tables.open_file(path)

    class PyTablesConnector(dc.Connector):
        connector_type = 'pytables'
        connection_class = PyTablesConnection

## Tables inspection

Datasette needs some data about your database so you have to provide it overwriting some methods in your custom connector. For that, the connector stores and instance of the class set in `connection_class` in the property `conn`, so you can use `self.conn` to access to your database in order to retrieve that data.

The methods that must be overwritten are:

* **table_names(self)**: a list of table names
* **hidden_table_names(self)**: a list of hidden table names
* **detect_spatialite(self)**: a boolean indicating if geometry_columns exists
* **view_names(self)**: a list of view names
* **table_count(self, table_name)**: an integer with the rows count of the table
* **table_info(self, table_name)**: a list of dictionaries with columns description
* **foreign_keys(self, table_name)**: a list of dictionaries with foreign keys description
* **table_exists(self, table_name)**: a boolean indicating if table exists in the database
* **table_definition(self, table_type, table_name)**: a string with a 'CREATE TABLE' sql definition
* **indices_definition(self, table_name)**: a list of strings with 'CREATE INDEX' sql definitions

## Returning results

Datasette uses SQL for specifying the queries, so your connector has to accept SQL and execute it. Overwriting `execute` method you can receive the query in SQL format and return some results.

The `Connector.execute()` method receives:

* **sql**: the query
* **params**: a dictionary with the params used in the query
* **truncate**: a boolean saying if the returned data can be separated in pages or not
* **custom_time_limit**: an integer with a time limit for the execution of the query in seconds
* **page_size**: the number of rows a page can contain
* **log_sql_errors**: a boolean saying if errors has to be logged

Probably, you'll need to parse the SQL query if your data container has its own style for queries, but other databases could work with the SQL queries without requiring any parsing.

Note: Sometimes, Datasette make queries to `sqlite_master`; you need to keep it in mind.

The `Connector.execute()` method has to return a tuple with:

* a list of rows; each row is a dictionary with the field name as key and the field value as value
* a boolean saying if the data is truncated, i.e., if we return all the rows or there are more rows than the maximum indicated in max_returned_rows
* a tuple with the description of the columns in the form `(('c1',), ('c2',), ...)`
