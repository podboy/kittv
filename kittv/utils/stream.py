# coding:utf-8

from enum import Enum
from errno import EAGAIN
from errno import EIO
from errno import ENOENT
import os
from time import time
from typing import List
from typing import Optional
from typing import Union
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen

from ipytv.playlist import IPTVAttr
from ipytv.playlist import IPTVChannel
from m3u8 import M3U8
from m3u8 import Segment
from m3u8 import load
import requests


class StreamType(Enum):
    M3U8 = "M3U8"
    MPD = "MPD"


class StreamTester:
    def __init__(self):
        self.__start: float = time()
        self.__bytes: int = 0

    @property
    def start(self) -> float:
        return self.__start

    @property
    def cost(self) -> float:
        return time() - self.start

    @property
    def receive(self) -> int:
        return self.__bytes

    @receive.setter
    def receive(self, value: int):
        self.__bytes = value

    @property
    def speed(self) -> int:
        return int(self.receive / self.cost)


class IPTVStream():
    MIN_BYTES_PER_SEC: int = 1024 * 128

    def __init__(self, channel: IPTVChannel, timeout: float,
                 speed_threshold: int):
        self.__channel: IPTVChannel = channel
        self.__timeout: float = timeout
        self.__speed_threshold: int = speed_threshold

    @property
    def timeout(self) -> float:
        return self.__timeout

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
    def speed_threshold(self) -> int:
        return self.__speed_threshold

    def request_head(self, timeout: Optional[float] = None) -> bool:
        try:
            response = requests.head(self.url, timeout=timeout or self.timeout)
            return True if response.status_code == 200 else False
        except requests.exceptions.RequestException:
            return False


class M3U8Stream(IPTVStream):
    TYPE: str = StreamType.M3U8.value

    def __init__(self, channel: IPTVChannel, timeout: float = 5.0):
        super().__init__(channel=channel, timeout=timeout,
                         speed_threshold=self.MIN_BYTES_PER_SEC)
        self.__transport: Optional[M3U8] = None

    @property
    def transport(self) -> M3U8:
        if self.__transport is None:
            self.__transport = load(uri=self.url, timeout=self.timeout)
        return self.__transport

    @property
    def available(self) -> bool:
        return self.speed > self.speed_threshold

    @property
    def speed(self) -> int:
        """units: bytes/sec
        """
        try:
            segments: List[Segment] = self.transport.segments
            if len(segments) < 1:
                return -ENOENT
            seg: Segment = segments[0]
            url: str = urljoin(seg.base_uri, seg.uri)
            tester: StreamTester = StreamTester()
            with urlopen(url=url, timeout=self.timeout) as resp:
                while tester.cost < self.timeout:
                    chunk = resp.read(10 * 1024)
                    if not chunk:
                        break
                    tester.receive += len(chunk)
            return tester.speed
        except URLError:
            return -EIO
        except TimeoutError:
            return -EAGAIN


class MPDStream(IPTVStream):
    TYPE: str = StreamType.MPD.value

    def __init__(self, channel: IPTVChannel, timeout: float = 5.0):
        super().__init__(channel=channel, timeout=timeout,
                         speed_threshold=self.MIN_BYTES_PER_SEC)

    @property
    def available(self) -> bool:
        return self.speed > self.speed_threshold

    @property
    def speed(self) -> int:
        """units: bytes/sec
        """
        return -EIO


STREAM = Union[M3U8Stream, MPDStream]


def load_stream(channel: IPTVChannel) -> STREAM:
    # os.path.splitext() cannot handle ".m3u8" correctly
    file_type: str = channel.url.rsplit(os.path.extsep, maxsplit=1)[1].lower()
    return {
        "mpd": MPDStream,
        "m3u8": M3U8Stream,
    }[file_type](channel)
