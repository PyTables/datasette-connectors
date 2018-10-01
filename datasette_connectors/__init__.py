import datasette
from datasette.cli import cli


# Monkey patching for original Datasette
def init(self, *args, **kwargs):
    print("Test")
    self.original_init(*args, **kwargs)

datasette.app.Datasette.original_init = datasette.app.Datasette.__init__
datasette.app.Datasette.__init__ = init


# Read external database connectors
from . import connectors
connectors.load_connectors()
