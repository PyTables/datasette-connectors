from .monkey import patch_datasette; patch_datasette()
from .connectors import ConnectorList; ConnectorList.load()
from datasette.cli import cli
