from datasette_connectors import monkey; monkey.patch_datasette()
from datasette_connectors.connectors import ConnectorList
from .dummy import DummyConnector
ConnectorList.add_connector('dummy', DummyConnector)

from datasette.app import Datasette
from datasette.utils.testing import TestClient
import os
import pytest
import tempfile
import contextlib


def populate_file(filepath):
    dummyfile = open(filepath, "w")
    dummyfile.write("This is a dummy file. We need something to force a SQLite error")
    dummyfile.close()


@contextlib.contextmanager
def make_app_client(
        max_returned_rows=None,
        config=None,
        is_immutable=False,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'dummy_tables.db')
        populate_file(filepath)
        if is_immutable:
            files = []
            immutables = [filepath]
        else:
            files = [filepath]
            immutables = []
        config = config or {}
        config.update({
            'default_page_size': 50,
            'max_returned_rows': max_returned_rows or 1000,
        })
        ds = Datasette(
            files,
            immutables=immutables,
            config=config,
        )
        client = TestClient(ds.app())
        client.ds = ds
        yield client


@pytest.fixture(scope='session')
def app_client():
    with make_app_client() as client:
        yield client


@pytest.fixture(scope='session')
def app_client_with_hash():
    with make_app_client(config={"hash_urls": True}, is_immutable=True) as client:
        yield client
