# coding:utf-8

import os
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

from ipytv.playlist import loadf
from ipytv.playlist import loadu

from .stream import STREAM
from .stream import load_stream


class Tunes():
    class Chain(List[STREAM]):
        def __init__(self, tvg_id: str):
            self.__tvg_id: str = tvg_id

        @property
        def tvg_id(self) -> str:
            return self.__tvg_id

        @property
        def available_stream(self) -> Tuple[STREAM]:
            return tuple(s for s in self if s.available())

    def __init__(self):
        self.__streams: List[STREAM] = []
        self.__channels: Dict[str, Tunes.Chain] = {}

    def __get(self, tvg_id: str) -> Chain:
        if tvg_id not in self.__channels:
            self.__channels.setdefault(tvg_id, Tunes.Chain(tvg_id=tvg_id))
        return self.__channels[tvg_id]

    def __len__(self) -> int:
        return len(self.channels)

    def __iter__(self) -> Iterator[Chain]:
        return iter(self.channels.values())

    def __contains__(self, tvg_id: str) -> bool:
        return tvg_id in self.channels

    def __getitem__(self, tvg_id: str) -> Chain:
        return self.channels[tvg_id]

    @property
    def streams(self) -> List[STREAM]:
        return self.__streams

    @property
    def channels(self) -> Dict[str, Chain]:
        return self.__channels

    def append(self, stream: STREAM):
        self.__streams.append(stream)
        self.__get(tvg_id=stream.tvg_id).append(stream)

    def extend(self, streams: List[STREAM]):
        for stream in streams:
            self.append(stream)

    @classmethod
    def loadfile(cls, filename: str) -> "Tunes":
        playlist: Tunes = Tunes()
        playlist.extend([load_stream(ch) for ch in loadf(filename=filename)])
        return playlist

    @classmethod
    def loadurl(cls, url: str) -> "Tunes":
        playlist: Tunes = Tunes()
        playlist.extend([load_stream(ch) for ch in loadu(url=url)])
        return playlist

    @classmethod
    def load(cls, filename_or_url: str) -> "Tunes":
        return cls.loadfile(filename_or_url) if os.path.isfile(
            filename_or_url) else cls.loadurl(filename_or_url)
