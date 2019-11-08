
"""Contains the base classes for sources."""

from abc import ABCMeta
from abc import abstractmethod


class SiteSource(metaclass=ABCMeta):
    """Base class for the site parser for video sources."""

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def language(self):
        pass

