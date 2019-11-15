"""Contains classes and functions to communicate with the TVDB API."""
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib import parse, request

from scotchbutter.util import environment

# TODO: Possibly move to a config file
AUTH_DATA = {
    'apikey': 'BFM8SU89SLQQHZU3',
    'username': 'unbecomingpigqqb',
    # 'userkey': 'OBVEZFJFUUOV1DBW'
    'userkey': 'B90E0DA644551A5C0A6BE9347BF55BBF'
}
API_URL = 'https://api.thetvdb.com'
TVDB_URL = 'https://thetvdb.com'
SUB_URLS = {
    'login': '/login',
    'refresh_token': '/refresh_token',
    'search_series': '/search/series?name={name}',
    'series': '/series/{series_id}',
    'episodes': '/series/{series_id}/episodes',
}
URLS = {key: request.urljoin(API_URL, path) for key, path in SUB_URLS.items()}
URLS['banners'] = request.urljoin(TVDB_URL, '/banners/')

# Sample string of date '1985-12-27'
# dates aren't zero padded anymore, so also '1990-9-2'
DATE_REGEX = re.compile(r'(?P<year>\d{4})-\d{1,2}-\d{1,2}')

class TvdbApi():
    """Provides an interface to query TVDB api."""

    def __init__(self):
        """Generate a new API instance."""
        self._token = None
        self._file_path = environment.get_settings_path()

    @property
    def token(self):
        """Generate new/use cached authentication token."""
        if self._token is None:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            data = bytes(json.dumps(AUTH_DATA), encoding='utf-8')
            req = request.Request(URLS['login'], headers=headers, data=data)
            try:
                response = request.urlopen(req)
            except request.HTTPError as error:
                if error.code == 401:
                    raise ConnectionRefusedError('Failed To Authenticate.')
                raise ConnectionError(f'Unexpected Response: {error.code}.')
            self._token = json.loads(response.read().decode('utf-8'))['token']
        return self._token

    @lru_cache()
    def _get(self, url: str, binary=False):
        """Post and return contents of an HTTP request."""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        req = request.Request(url, headers=headers)
        try:
            response = request.urlopen(req)
        except request.HTTPError as error:
            if error.code == 404:
                raise LookupError('There are no data for this term.')
            raise ConnectionError(f'Unexpected Response: {error.code}.')
        if binary is True:
            contents = response.read() or None
        else:
            contents = json.loads(response.read().decode('utf-8'))
        return contents

    def get_series(self, series_id: int):
        """Query TVDB for information about a series."""
        response = self._get(URLS['series'].format(series_id=series_id))
        response['data']['seriesId'] = response['data']['id']
        return TvdbSeries(response['data'], self)

    def get_episodes(self, series_id: int):
        """Get all episode information for a series."""
        url = URLS['episodes'].format(series_id=series_id)
        raw_data = self._get(url)['data']
        episode_data = list(raw_data)
        tvdb_page_size = 100
        page = 1
        while len(raw_data) == tvdb_page_size:
            page += 1
            url = URLS['episodes'].format(series_id=series_id) + f'?page={page}'
            try:
                raw_data = self._get(url)['data']
            except LookupError:
                # When (total results) % tvdb_page_size == 0
                break
            episode_data += raw_data
        return episode_data

    def search_series(self, search_string: str):
        """Search TVDB for matching shows."""
        url = URLS['search_series'].format(name=parse.quote(search_string))
        raw_data = self._get(url)['data']
        found_series = {}
        for series in raw_data:
            if not series['seriesName']:
                # Apparently this can be a thing.
                continue
            series_ident = f"{series['seriesName']}"
            date = DATE_REGEX.match(series['firstAired'] or '')
            if date:
                year = f" ({date.groupdict()['year']})"
                if not series_ident.endswith(year):
                    series_ident += year
            found_series[series_ident] = TvdbSeries(series, self)
        return found_series

    @lru_cache()
    def download(self, path: str, output_file: Path = None):
        """Download a file from TVDB."""
        url = request.urljoin(URLS['banners'], path)
        output_file = output_file or self._file_path.joinpath(path)
        if not Path.is_file(output_file):
            data = self._get(url, binary=True)
            if data is None:
                # Sometimes files come back with 0 bytes instead of 404 error
                # We are going to pretend they don't exist for right now.
                output_file = None
            else:
                if not Path.is_dir(output_file.parent):
                    Path.mkdir(output_file.parent, parents=True)
                with open(output_file, 'wb') as f:
                    f.write(data)
        return output_file


class TvdbSeries():
    """Container for a information about a TV Show."""

    def __init__(self, series_data, tvdb_api):
        """Create a TV Series container."""
        self._tvdb_api = tvdb_api
        self._series_data = series_data
        self.series_id = series_data['id']
        self.series_name = series_data['seriesName']
        self.series_ident = series_data['seriesName']
        self._episodes = None
        date = DATE_REGEX.match(self._series_data['firstAired'] or '')
        if date:
            year = f" ({date.groupdict()['year']})"
            # The series_ident will always include the year
            if not self._series_data['seriesName'].endswith(year):
                self.series_ident += year

    def __getitem__(self, key):
        if key in self._series_data:
            return self._series_data[key]
        raise KeyError(key)

    def __str__(self):
        return self.series_ident

    def __repr__(self):
        return f'{self.series_ident} -- seriesId: {self.series_id}'

    @property
    def episodes(self):
        """Find all known episodes of the series."""
        if self._episodes is None:
            episodes_data = self._tvdb_api.get_episodes(self.series_id)
            episodes = []
            for episode_data in sorted(episodes_data, key=lambda x:
                                       (x['airedSeason'], x['airedEpisodeNumber'])):
                episodes.append(Episode(episode_data, self, self._tvdb_api))
            self._episodes = episodes
        return self._episodes

    @property
    def banner(self):
        """Download the series banner from TVDB."""
        return self._tvdb_api.download(self._series_data['banner'])


class Episode():
    """Container for an episode of a series."""

    def __init__(self, episode_data, series, tvdb_api):
        """Create an episode container."""
        self._episode_data = episode_data
        self._series = series
        self._tvdb_api = tvdb_api
        self.series_name = series.series_name
        self.series_ident = series.series_ident
        self.series_id = series.series_id
        self.episode_number = episode_data['airedEpisodeNumber']
        self.season = episode_data['airedSeason']
        self.name = self._episode_data['episodeName']

    def __getitem__(self, key):
        if key in self._episode_data:
            return self._episode_data[key]
        raise KeyError(key)

    def __str__(self):
        return f'{self.series_ident} - S{self.season:02d}E{self.episode_number:02d} - {self.name}'

    @property
    def thumbnail(self):
        """Download the episode thumbnail from TVDB."""
        filename = self._episode_data['filename']
        if filename:
            thumbnail = self._tvdb_api.download(filename)
        else:
            thumbnail = None
        return thumbnail
