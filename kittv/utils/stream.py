# coding:utf-8

from typing import Any
from typing import Dict
from typing import Iterator
from typing import Optional

from ffmpeg import Error as fferror
from ffmpeg import probe as ffprobe
from ipytv.playlist import IPTVAttr
from ipytv.playlist import IPTVChannel
from xkits import CacheAtom
from xkits import singleton


class StreamProber():
    MINIMUM = 1800  # 30 minutes
    DEFAULT = 10800  # 3 hours
    MAXIMUM = 86400  # 1 day

    class Format:
        def __init__(self, data: Dict[str, Any]):
            self.__data: Dict[str, Any] = data

        @property
        def probe_score(self) -> int:
            return self.__data.get("probe_score", 0)

    def __init__(self, url: str, timeout: float):
        self.__ffprobe: Optional[CacheAtom[Dict[str, Any]]] = None
        self.__timeout: float = max(1.0, timeout)  # probe timeout
        self.__lifetime: float = self.DEFAULT  # data lifetime
        self.__success: bool = False
        self.__url: str = url

    def __str__(self) -> str:
        return f"IPTV Stream Prober URL={self.url}"

    @property
    def url(self) -> str:
        return self.__url

    @property
    def ffprobe(self) -> Dict[str, Any]:
        if self.__ffprobe is None or self.__ffprobe.expired:
            try:
                data = ffprobe(self.url, timeout=int(self.__timeout * 1000000))
                self.__ffprobe = CacheAtom(data=data, lifetime=self.__lifetime)
                self.__success = True
            except fferror:
                self.__ffprobe = CacheAtom(data={}, lifetime=self.__lifetime)
                self.__success = False
            finally:
                self.__timeout = min(self.__timeout if self.__success else self.__timeout + 0.5, 30.0)  # noqa:E501
                self.__lifetime *= 1.15 if self.__success or self.__timeout >= 30 else 0.85  # noqa:E501
        return self.__ffprobe.data

    @property
    def format(self) -> Format:
        return self.Format(self.ffprobe.get("format", {}))


@singleton
class StreamProberPool():
    def __init__(self):
        self.__probers: Dict[str, StreamProber] = {}

    def __len__(self) -> int:
        return len(self.__probers)

    def __iter__(self) -> Iterator[StreamProber]:
        return iter(self.__probers.values())

    def __getitem__(self, url: str) -> StreamProber:
        return self.__probers[url]

    def __contains__(self, url: str) -> bool:
        return url in self.__probers

    def alloc(self, url: str, timeout: float) -> StreamProber:
        if url not in self.__probers:
            self.__probers.setdefault(url, StreamProber(url, timeout))
        return self.__probers[url]


STREAMPROBERS: StreamProberPool = StreamProberPool()


class IPTVStream():

    def __init__(self, channel: IPTVChannel, timeout: float = 3.0):
        self.__prober: StreamProber = STREAMPROBERS.alloc(channel.url, timeout)
        self.__channel: IPTVChannel = channel

    def __str__(self) -> str:
        return f"IPTVStream {self.name} URL={self.url}"

    @property
    def url(self) -> str:
        return self.__channel.url

    @property
    def name(self) -> str:
        return self.__channel.name

    @property
    def tvg_id(self) -> str:
        return self.__channel.attributes.get(IPTVAttr.TVG_ID.value, "")

    @property
    def tvg_name(self) -> str:
        return self.__channel.attributes.get(IPTVAttr.TVG_NAME.value, "")

    @property
    def available(self) -> bool:
        '''stream is available'''
        return self.score >= 90

    @property
    def score(self) -> int:
        """probe score"""
        return self.__prober.format.probe_score
