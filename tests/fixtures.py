from datasette_connectors import monkey; monkey.patch_datasette()
from datasette_connectors import connectors
from . import dummy
connectors.db_connectors['dummy'] = dummy

from datasette.app import Datasette
import os
import pytest
import tempfile

@pytest.fixture(scope='session')
def app_client(max_returned_rows=None):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'dummy_tables.db')
        populate_file(filepath)
        ds = Datasette(
            [filepath],
            config={
                'default_page_size': 50,
                'max_returned_rows': max_returned_rows or 1000,
            }
        )
        client = ds.app().test_client
        client.ds = ds
        yield client


def populate_file(filepath):
    dummyfile = open(filepath, "w")
    dummyfile.write("This is a dummy file. We need something to force a SQLite error")
    dummyfile.close()
