from .monkey import patch_datasette; patch_datasette()
from .connectors import load_connectors; load_connectors()
from datasette.cli import cli
