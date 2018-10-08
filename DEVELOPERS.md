# How to make connectors for other data sources?

With Datasette-Connectors you can use [Datasette](https://github.com/simonw/datasette) for publishing data in your own format, not only SQLite, to the Internet with a JSON API. For this, you have to make connectors using the interface that is described here.

## Tables inspection

First of all, you need to implement a special method called `inspect` that receives the path of the file as an argument and returns a tuple formed by a dictionary with tables info, a list with views name and a string identifying the connector. Each entry in the dictionary for tables info has the next structure:

    tables['table_name'] = {
        'name': 'table_name',
        'columns': ['c1', 'c2'],
        'primary_keys': [],
        'count': 100,
        'label_column': None,
        'hidden': False,
        'fts_table': None,
        'foreign_keys': {'incoming': [], 'outgoing': []}

This structure is used in [Datasette-PyTables](https://github.com/PyTables/datasette-pytables). In your case, you may need additional entries like primary keys or foreign keys.

## Returning results

Datasette uses SQL for specifying the queries, so your connector has to accept SQL and execute it. The next class and methods are needed:

    class Connection:
        def __init__(self, path):
            ...

        def execute(self, sql, params=None, truncate=False, page_size=None, max_returned_rows=None):
            ...

The `Connection.execute()` method receives:

* **sql**: the query
* **params**: a dictionary with the params used in the query
* **truncate**: a boolean saying if the returned data can be separated in pages or not
* **page_size**: the number of rows a page can contain
* **max_returned_rows**: the maximum number of rows Datasette expects

Probably, you'll need to parse the SQL query if your data container has its own style for queries, but other databases could work with the SQL queries without requiring any parsing.

Note: Sometimes, Datasette make queries to `sqlite_master`; you need to keep it in mind.

The `Connection.execute()` method has to return a tuple with:

* a list of rows (Datasette expects something similar to SQLite rows)
* a boolean saying if the data is truncated, i.e., if we return all the rows or there are more rows than the maximum indicated in max_returned_rows
* a tuple with the description of the columns in the form `(('c1',), ('c2',), ...)`

## Rows format

Datasette receives the results from the queries with SQLite row instances, so you need to return your rows in a similar way.

For example, if you have the next query:

    SELECT name FROM persons

you need to return an object that allows to do things like:

    row[0] == 'Susan'
    row['name'] == 'Susan'
    [c for c in row] == ['Susan']
    json.dumps(row)

Datasette-Connectors provides you a Row class that extends `list` object to get it, but as long as you implement a similar interface, you can develop your own implementation too.
