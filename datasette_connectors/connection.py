from .cursor import Cursor


class Connection:
    def __init__(self, path, connector_class):
        self.path = path
        self.connector_class = connector_class

    def execute(self, *args, **kwargs):
        cursor = Cursor(self)
        cursor.execute(*args, **kwargs)
        return cursor

    def cursor(self):
        return Cursor(self)

    def set_progress_handler(self, handler, n):
        pass
