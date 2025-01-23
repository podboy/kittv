# coding:utf-8

from typing import Any
from typing import Dict
from typing import Optional

from ffmpeg import Error as fferror
from ffmpeg import probe as ffprobe
from ipytv.playlist import IPTVAttr
from ipytv.playlist import IPTVChannel
import requests
from xkits import CacheAtom


class StreamProber(CacheAtom[Dict[str, Any]]):
    PERIOD = 300

    class Format:
        def __init__(self, data: Dict[str, Any]):
            self.__data: Dict[str, Any] = data

        @property
        def probe_score(self) -> int:
            return self.__data["probe_score"]

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(data=data or {}, lifetime=self.PERIOD)
        self.__format: StreamProber.Format = self.Format(self.data.get("format", {}))  # noqa:E501
        self.__success: bool = data is not None

    @property
    def success(self) -> bool:
        return self.__success

    @property
    def format(self) -> Format:
        return self.__format

    @classmethod
    def ffprobe(cls, url: str, timeout: float) -> "StreamProber":
        try:
            return cls(ffprobe(url, timeout=int(timeout * 1000000)))
        except fferror:
            return cls()


class IPTVStream():

    def __init__(self, channel: IPTVChannel, timeout: float = 8.0):
        self.__probe: Optional[StreamProber] = None
        self.__channel: IPTVChannel = channel
        self.__timeout: float = timeout

    @property
    def url(self) -> str:
        return self.channel.url

    @property
    def name(self) -> str:
        return self.channel.name

    @property
    def tvg_id(self) -> str:
        return self.channel.attributes.get(IPTVAttr.TVG_ID.value, "")

    @property
    def tvg_name(self) -> str:
        return self.channel.attributes.get(IPTVAttr.TVG_NAME.value, "")

    @property
    def channel(self) -> IPTVChannel:
        return self.__channel

    @property
    def timeout(self) -> float:
        return self.__timeout

    @property
    def available(self) -> bool:
        return self.probe.success

    @property
    def probe(self) -> StreamProber:
        if self.__probe is None or self.__probe.expired:
            self.__probe = StreamProber.ffprobe(self.url, self.timeout)
        return self.__probe

    @property
    def score(self) -> int:
        """probe score"""
        return self.probe.format.probe_score

    def request_head(self, timeout: Optional[float] = None) -> bool:
        try:
            response = requests.head(self.url, timeout=timeout or self.timeout)
            return True if response.status_code == 200 else False
        except requests.exceptions.RequestException:
            return False
