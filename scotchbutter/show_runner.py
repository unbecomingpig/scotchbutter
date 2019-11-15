#!/usr/bin/env python
"""Provide a debugging front end for maintaining the database."""

import argparse
import logging
import sys

from scotchbutter.util import tvdb

# from scotchbutter.util import database

logger = logging.getLogger(__name__)


class FatalError(Exception):
    """Manually raised excpetions that should end the script."""


def parse_args() -> argparse.Namespace:
    """Parse initialization arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True
    # Arguments for adding a series to the database.
    add_parser = subparsers.add_parser('add', help='Add a series_id to the library')
    add_parser.add_argument('series_id', type=int, help='The TVDB SeriesId')
    # Arguments for removing a series from the database.
    remove_parser = subparsers.add_parser('remove', help='Remove a series_id from the library')
    remove_parser.add_argument('series_id', type=int, help='The TVDB SeriesId')
    # Arguments for searching TVDB for a series.
    search_parser = subparsers.add_parser('search', help='Search TVDB for a TV series')
    search_parser.add_argument('search_text', nargs='+', type=str, help='Text to search on TVDB.')
    # Arguments for updating the series information in the database.
    update_parser = subparsers.add_parser('update',
                                          help='Update series/episode information in the library')
    update_parser.add_argument('series_id', type=int, help='The TVDB SeriesId')
    # Arguments for displaying information about a show.
    info_parser = subparsers.add_parser('info', help='Display information about a series')
    info_parser.add_argument('series_id', type=int, help='The TVDB SeriesId')
    group = info_parser.add_mutually_exclusive_group()
    group.add_argument('--overview', action='store_true', help='Show series overview')
    group.add_argument('--episode', type=int, help='Show episode overview')
    # Arguments for downloading artwork for a show.
    artwork_parser = subparsers.add_parser('artwork', help='Download artwork for a series')
    artwork_parser.add_argument('series_id', type=int, help='The TVDB SeriesId')
    artwork_parser.add_argument('--banner', action='store_true', help='Download the series banner')
    artwork_parser.add_argument('--thumbs', action='store_true',
                                help='Download the episode thumbs')
    args = parser.parse_args()
    if args.action == 'search':
        args.search_text = ' '.join(args.search_text)
    return args


def check_implemented_actions(args: argparse.Namespace) -> None:
    """Check if a argument action has been implemented yet.

    This function will eventually be removed when functionality is fully implemented.
    """
    notimplemented_actions = {
        'add': set(),
        'remove': set(),
        'search': set(),
        'info': {'series_id', 'overview', 'episode'},
        'artwork': {'series_id', 'banner', 'thumbs'},
    }
    args_dict = vars(args)
    for action in notimplemented_actions[args_dict['action']]:
        if args_dict[action]:
            raise NotImplementedError(f'{args.action} {action} is not implemented')

def search_series(tvdb_api: tvdb.TvdbApi, search_text: str) -> dict:
    """Search TVDB for shows."""
    try:
        results = tvdb_api.search_series(search_text)
    except LookupError:
        results = {}
    if not results:
        raise FatalError(f'TVDB returned no results for search string: "{search_text}"')
    for series_ident, series in sorted(results.items()):
        print(f'{series} -- SeriesId: {series.id}')



def main():
    """Run the showrunner script."""
    args = parse_args()
    check_implemented_actions(args)
    tvdb_api = tvdb.TvdbApi()
    try:
        if args.action == 'search':
            search_series(tvdb_api, args.search_text)
    except FatalError as error:
        print(error)
        sys.exit(2)


if __name__ == '__main__':
    main()
