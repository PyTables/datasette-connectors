from .monkey import patch_datasette; patch_datasette()
from .connectors import load; load()
from datasette.cli import cli
