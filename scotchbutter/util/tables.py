"""Contains the database schema helpers."""


class Column():
    """Helper to manage table column data."""

    def __init__(self, name, datatype, constraint=None):
        self.name = name
        self.datatype = datatype
        self.constraint = constraint
        # TODO: Add validity checks to for name, datatype, and constraint

    @property
    def create_text(self):
        """Generate the column string used the CREATE TABLE query."""
        return ' '.join([self.name, self.datatype, self.constraint or ''])


class Table():
    """Helper class to manage table data."""

    def __init__(self, table_name: str):
        """Create a container to help manage an SQL table."""
        self.table_name = table_name
        self.columns = []

    def add_column(self, column: Column):
        """Add a Column type object to the table."""
        self.columns.append(column)

    @property
    def create_table_string(self):
        """Generate an SQL query to create the table in a database."""
        columns = ', '.join([column.create_text for column in self.columns])
        return f"CREATE TABLE IF NOT EXISTS '{self.table_name}' ({columns});"

    @property
    def insert_string(self):
        """Generate an SQL query to insert values into a database."""
        columns = ', '.join([column.name for column in self.columns])
        values = ','.join('?'*len(self.columns))
        return f"INSERT OR REPLACE INTO '{self.table_name}' ({columns}) VALUES({values})"


LIBRARY_COLUMNS = (
    Column('seriesId', 'INTEGER', 'PRIMARY KEY'),
    Column('airsDayOfWeek', 'TEXT', None),
    Column('airsTime', 'TEXT', None),
    Column('banner', 'TEXT', None),
    Column('firstAired', 'TEXT', None),
    Column('imdbId', 'TEXT', None),
    Column('overview', 'TEXT', None),
    Column('seriesName', 'TEXT', 'NOT NULL'),
)

SHOW_COLUMNS = (
    Column('id', 'INTEGER', 'PRIMARY KEY'),
    Column('airedSeason', 'INTEGER', 'NOT NULL'),
    Column('airedEpisodeNumber', 'INTEGER', 'NOT NULL'),
    Column('episodeName', 'TEXT', 'NOT NULL'),
    Column('firstAired', 'TEXT', None),
    Column('absoluteNumber', 'INTEGER', None),
    Column('dvdSeason', 'INTEGER', None),
    Column('dvdEpisodeNumber', 'INTEGER', None),
    Column('imdbId', 'TEXT', None),
    Column('seriesId', 'INTEGER', 'NOT NULL'),
    Column('filename', 'TEXT', None),
    Column('overview', 'TEXT', None),
)
