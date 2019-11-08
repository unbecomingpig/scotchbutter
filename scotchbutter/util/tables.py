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
        return f'CREATE TABLE [IF NOT EXISTS] {self.table_name} ({columns});'


class ShowTable(Table):
    """Helper class to manage a single show's data."""

    def __init__(self, seriesId):
        """Create a Table for a show with seriesId."""
        super(ShowTable, self).__init__(seriesId)
        self.add_column(Column('id', 'INTEGER'))
        self.add_column(Column('absoluteNumber', 'INTEGER'))
        self.add_column(Column('airedEpisodeNumber', 'INTEGER'))
        self.add_column(Column('airedSeason', 'INTEGER'))
        self.add_column(Column('dvdEpisodeNumber', 'INTEGER'))
        self.add_column(Column('dvdSeason', 'INTEGER'))
        self.add_column(Column('episodeName', 'TEXT'))
        self.add_column(Column('firstAired', 'TEXT'))
        self.add_column(Column('imdbId', 'TEXT'))
        self.add_column(Column('overview', 'TEXT'))
        self.add_column(Column('seriesId', 'INTEGER'))
        self.add_column(Column('ThumbFile', 'TEXT'))


LIBRARY_TABLE = Table('library')
LIBRARY_TABLE.add_column(Column('seriesId', 'INTEGER', 'PRIMARY KEY'))
LIBRARY_TABLE.add_column(Column('airsDayOfWeek', 'TEXT'))
LIBRARY_TABLE.add_column(Column('airsTime', 'TEXT'))
LIBRARY_TABLE.add_column(Column('banner', 'TEXT'))
LIBRARY_TABLE.add_column(Column('firstAired', 'TEXT'))
LIBRARY_TABLE.add_column(Column('imdbId', 'TEXT'))
LIBRARY_TABLE.add_column(Column('overview', 'TEXT'))
LIBRARY_TABLE.add_column(Column('seriesName', 'TEXT', 'NOT NULL'))
