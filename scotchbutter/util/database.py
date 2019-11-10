"""Contains functions to help facilitate reading/writing from a database.

NOTE: Currently only supporting sqlite databases
"""

import logging
import sqlite3

from scotchbutter.util import environment
from scotchbutter.util import tables

logger = logging.getLogger(__name__)

DB_FILENAME = 'tvshows.sqlite'


class DBInterface():
    """Provides a contraced API to query the DataBase.

    Providing a contracted API allows for an transparent backend
    changes. # TODO: Add DB connections beyond sqlite.
    """

    library_name = 'library'

    def __init__(self, db_file: str = DB_FILENAME):
        """Create an interface to query the DataBase."""
        self._settings_path = environment.get_settings_path()
        self._db_file = self._settings_path.joinpath(db_file)
        self._conn = None
        self._cursor = None
        self.library_table = self.create_table(self.library_name, tables.LIBRARY_COLUMNS)
        self.close()

    @property
    def conn(self):
        """Create a DB connection if it doesn't already exist."""
        if self._conn is None:
            self.connect()
        return self._conn

    @property
    def cursor(self):
        """Create a cursor to interact with the database."""
        if self._cursor is None:
            self.connect()
        return self._cursor

    @property
    def existing_tables(self):
        """List tables currently in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        results = self.cursor.execute(query)
        table_names = sorted([name for result in results for name in result])
        return table_names

    def connect(self):
        """Create a new connection to DB."""
        # If the database file doesn't exist, this will create it.
        self._conn = sqlite3.connect(self._db_file)
        self._cursor = self.conn.cursor()

    def close(self, commit: bool = True):
        """Close the DB connections."""
        if self._conn is not None:
            if commit is True:
                self.conn.commit()
            self.conn.close()
        self._conn = None
        self._cursor = None

    def __enter__(self):
        """Context management protocol."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes any existing DB connection."""
        self.close()

    def create_table(self, name, columns):
        """Create a table in the database."""
        table = tables.Table(name)
        for column in columns:
            table.add_column(column)
        if name not in self.existing_tables:
            self.cursor.execute(table.create_table_string)
        return table

    def add_series(self, series):
        """Add a series to the database."""
        values = [getattr(series, column.tvdb_field) for column in self.library_table.columns]
        self.cursor.execute(self.library_table.insert_string, values)
        show_table = self.create_table(series.series_id, tables.SHOW_COLUMNS)
        episodes = []
        for episode in series.episodes:
            values = [episode[column.tvdb_field] for column in show_table.columns]
            episodes.append(values)
        self.cursor.executemany(show_table.insert_string, episodes)
