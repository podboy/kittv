# coding:utf-8

import os
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

from ipytv.playlist import M3UPlaylist
from ipytv.playlist import loadf
from ipytv.playlist import loadu

from .stream import IPTVStream


class Tunes():
    class Chain(List[IPTVStream]):
        def __init__(self, tvg_id: str):
            self.__tvg_id: str = tvg_id

        @property
        def tvg_id(self) -> str:
            return self.__tvg_id

        @property
        def available_stream(self) -> Tuple[IPTVStream, ...]:
            return tuple(s for s in self if s.available)

    def __init__(self):
        self.__streams: List[IPTVStream] = []
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
    def streams(self) -> List[IPTVStream]:
        return self.__streams

    @property
    def channels(self) -> Dict[str, Chain]:
        return self.__channels

    @property
    def playlist(self) -> M3UPlaylist:
        playlist: M3UPlaylist = M3UPlaylist()
        for key in sorted(self.channels.keys()):
            streams: List[IPTVStream] = self.channels[key]
            for stream in sorted(streams, key=lambda s: s.channel.name):
                playlist.append_channel(stream.channel)
        return playlist

    def append(self, stream: IPTVStream):
        self.__streams.append(stream)
        self.__get(tvg_id=stream.tvg_id).append(stream)

    def extend(self, streams: List[IPTVStream]):
        for stream in streams:
            self.append(stream)

    def dumpfile(self, filename: str) -> bool:
        if not filename.endswith(".m3u"):
            filename += ".m3u"
        abspath: str = os.path.abspath(filename)
        dirname: str = os.path.dirname(abspath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(abspath, "w") as whdl:
            whdl.write(self.dumpstr())
        return True

    def dumpstr(self) -> str:
        return self.playlist.to_m3u_plus_playlist()

    @classmethod
    def loadfile(cls, filename: str) -> "Tunes":
        playlist: Tunes = Tunes()
        playlist.extend([IPTVStream(ch) for ch in loadf(filename=filename)])
        return playlist

    @classmethod
    def loadurl(cls, url: str) -> "Tunes":
        playlist: Tunes = Tunes()
        playlist.extend([IPTVStream(ch) for ch in loadu(url=url)])
        return playlist

    @classmethod
    def load(cls, file_or_url: str) -> "Tunes":
        return cls.loadfile(file_or_url) if os.path.isfile(
            file_or_url) else cls.loadurl(file_or_url)
