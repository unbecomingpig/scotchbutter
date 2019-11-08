"""Contains functions to interact with the host system's environment."""

import os
from pathlib import Path
from functools import lru_cache

APP_NAME = 'scotchbutter'

@lru_cache()
def get_settings_path(app_name: str = APP_NAME) -> Path:
    """Find the base location of the setting folder.

    The path will be informational, not an indication of it's actual existance.
    """
    if os.name == 'nt':
        base_path = Path(os.getenv('APPDATA'))
    elif os.name == 'posix':
        base_path = Path.home()
        # Make the folder hidden by the '.' prefix
        app_name = f'.{app_name}'
    elif os.name == 'java':
        raise NotImplementedError('Java systems are not currently supported.')
    else:
        raise NotImplementedError('Unknown OS type is not supported.')
    settings_path = base_path.joinpath(app_name)
    # If the setting_path doesn't exist, create it.
    if settings_path.is_dir() is False:
        settings_path.mkdir()
    return settings_path
