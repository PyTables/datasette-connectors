from .cursor import Cursor


class Connection:
    def __init__(self, path, connector):
        self.path = path
        self.connector = connector

    def execute(self, *args, **kwargs):
        cursor = Cursor(self)
        cursor.execute(*args, **kwargs)
        return cursor

    def cursor(self):
        return Cursor(self)

    def set_progress_handler(self, handler, n):
        pass
