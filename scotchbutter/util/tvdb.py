"""Contains classes and functions to communicate with the TVDB API."""
from urllib import request
from functools import lru_cache

import json

#TODO: Possibly move to a config file
AUTH_DATA = {
    'apikey': 'BFM8SU89SLQQHZU3',
    'username': 'unbecomingpigqqb',
    'userkey': 'OBVEZFJFUUOV1DBW'
}
TVDB_URL = 'https://api.thetvdb.com'
SUB_URLS = {
    'login': '/login',
    'refresh_token': '/refresh_token',
    'search_series': '/search/series',
    'series': '/series/{tvdb_id}',
    'episodes': '/series/{tvdb_id}/episodes',
}
URLS = {key: request.urljoin(TVDB_URL, path) for key, path in SUB_URLS.items()}


class TvdbApi():
    """Provides an interface to query TVDB api."""

    def __init__(self):
        """Generate a new API instance."""
        self._token = None

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
    def _get(self, url):
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
        return json.loads(response.read().decode('utf-8'))

    def get_series(self, tvdb_id):
        """Query TVDB for information about a series."""
        response = self._get(URLS['series'].format(tvdb_id=tvdb_id))
        return TvdbSeries(response['data'], self)

    def get_episodes(self, tvdb_id):
        """Get all episode information for a series."""
        url = URLS['episodes'].format(tvdb_id=tvdb_id)
        raw_data = self._get(url)['data']
        episode_data = list(raw_data)
        tvdb_page_size = 100
        page = 1
        while len(raw_data) == tvdb_page_size:
            page += 1
            url = URLS['episodes'].format(tvdb_id=tvdb_id) + f'?page={page}'
            try:
                raw_data = self._get(url)['data']
            except LookupError:
                # When (total results) % tvdb_page_size == 0
                break
            episode_data += raw_data
        return episode_data


class TvdbSeries():
    """Container for a information about a TV Show."""

    def __init__(self, tvdb_data, tvdb_api):
        """Create a TV Series container."""
        self._tvdb_api = tvdb_api
        self._tvdb_data = tvdb_data
        self.series_id = tvdb_data['id']
        self.series_name = tvdb_data['seriesName']

    def __getattr__(self, key):
        if key in self._tvdb_data:
            return self._tvdb_data[key]
        raise KeyError(key)

    def __str__(self):
        return self._tvdb_data['seriesName']

    @property
    def episodes(self):
        """Find all known episodes of the series."""
        return self._tvdb_api.get_episodes(self.series_id)
