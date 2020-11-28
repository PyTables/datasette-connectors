# datasette-connectors

[Datasette](https://github.com/simonw/datasette) is a Python module which provides a web interface and a JSON API for SQLite files. But, in conjuntion with Datasette-Connectors, it can accept external connectors for any kind of database files, so you can develop your own connector for your favourite data container if you want (read [developers doc](https://github.com/PyTables/datasette-connectors/blob/master/DEVELOPERS.md)).

## Installation

Run `pip install datasette-connectors` to install both Datasette and Datasette-Connectors. Easy as pie!

## Usage

You can use Datasette from the console in the traditional way:

    datasette serve path/to/data.h5

This will start a web server on port 8001; then you can access to your data visiting [http://localhost:8001/](http://localhost:8001/)

Or you can use Datasette in your own Python programs:

    from datasette_connectors import monkey; monkey.patch_datasette()
    from datasette_connectors.connectors import ConnectorList; ConnectorList.load()

For that, you need to patch the original Datasette and load the external connectors.

Read the [Datasette documentation](http://datasette.readthedocs.io/en/latest/) for more advanced options.
