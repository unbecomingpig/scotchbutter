"""Contains functions to help facilitate reading/writing from a database.

NOTE: Currently only supporting sqlite databases
"""

import logging
import sqlite3

from scotchbutter.util import environment

logger = logging.getLogger(__name__)

DB_FILENAME = 'tvshows.sqlite'


class DBInterface():
    """Provides a contraced API to query the DataBase.

    Providing a contracted API allows for an transparent backend
    changes. # TODO: Add DB connections beyond sqlite.
    """

    def __init__(self, db_file: str = DB_FILENAME):
        """Create an interface to query the DataBase."""
        self._settings_path = environment.get_settings_path()
        self._db_file = self._settings_path.joinpath(db_file)
        # Don't create the connection until it is actually called
        self._conn = None
        self._cursor = None

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
