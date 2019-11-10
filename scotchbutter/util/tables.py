"""Contains the database schema helpers."""


class Column():
    """Helper to manage table column data."""

    def __init__(self, name, datatype, constraint=None, tvdb_field=None):
        self.name = name
        self.datatype = datatype
        self.constraint = constraint
        self.tvdb_field = tvdb_field
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
    Column('seriesId', 'INTEGER', 'PRIMARY KEY', 'id'),
    Column('airsDayOfWeek', 'TEXT', None, 'airsDayOfWeek'),
    Column('airsTime', 'TEXT', None, 'airsTime'),
    Column('banner', 'TEXT', None, 'banner'),
    Column('firstAired', 'TEXT', None, 'firstAired'),
    Column('imdbId', 'TEXT', None, 'imdbId'),
    Column('overview', 'TEXT', None, 'overview'),
    Column('seriesName', 'TEXT', 'NOT NULL', 'seriesName'),
)

SHOW_COLUMNS = (
    Column('episodeId', 'INTEGER', 'PRIMARY KEY', 'id'),
    Column('absoluteNumber', 'INTEGER', None, 'absoluteNumber'),
    Column('airedEpisodeNumber', 'INTEGER', 'NOT NULL', 'airedEpisodeNumber'),
    Column('airedSeason', 'INTEGER', 'NOT NULL', 'airedSeason'),
    Column('dvdEpisodeNumber', 'INTEGER', None, 'dvdEpisodeNumber'),
    Column('dvdSeason', 'INTEGER', None, 'dvdSeason'),
    Column('episodeName', 'TEXT', 'NOT NULL', 'episodeName'),
    Column('firstAired', 'TEXT', None, 'firstAired'),
    Column('imdbId', 'TEXT', None, 'imdbId'),
    Column('overview', 'TEXT', None, 'overview'),
    Column('seriesId', 'INTEGER', 'NOT NULL', 'seriesId'),
    Column('thumbFile', 'TEXT', None, 'filename'),
)
