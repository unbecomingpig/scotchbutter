from urllib import request
from collections import defaultdict

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

    def __init__(self):
        self._token = None

    @property
    def token(self):
        if self._token is None:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            data = bytes(json.dumps(AUTH_DATA), encoding='utf-8')
            req = request.Request(URLS['login'], headers=headers, data=data)
            response = request.urlopen(req)
            if response.code == 401:
                raise ConnectionRefusedError('Failed To Authenticate.')
            elif response.code != 200:
                raise ConnectionError('Unexpected Response.')
            self._token = json.loads(response.read().decode('utf-8'))['token']
        return self._token

    def _get(self, url):
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        if response.code == 404:
            raise LookupError('There are no data for this term.')
        elif response.code != 200:
            raise ConnectionError('Unexpected Response.')
        return json.loads(response.read().decode('utf-8'))

    def get_series(self, tvdb_id):
        response = self._get(URLS['series'].format(tvdb_id=tvdb_id))
        return response['data']

    def get_episodes(self, tvdb_id):
        response = self._get(URLS['episodes'].format(tvdb_id=tvdb_id))
        episode_data = response['data']
        # Specials are weird and going to be put in a special season 00 list
        episodes = {'00': []}
        for episode in episode_data:
            # Going with Aired numbers
            # TODO: Add option to use DVD numbers
            # Converting to zero padded strings for ease of use
            season_number = f'{episode.get("airedSeason", 0):02d}'
            episode_number = f'{episode.get("airedEpisodeNumber", 0):02d}'
            episodes[season_number] = episodes.get(season_number, {})
            if season_number == '00':
                episodes[season_number].append(episode)
            else:
                # Assumption: season_number + episode_number is unique
                episodes[season_number][episode_number] = episode
        return episodes
