# coding:utf-8

import os
from typing import Optional
from typing import Union

from ipytv.playlist import IPTVAttr
from ipytv.playlist import IPTVChannel
from m3u8 import M3U8
from m3u8 import load
import requests


class IPTVStream():
    def __init__(self, channel: IPTVChannel):
        self.__channel: IPTVChannel = channel

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

    def request(self, timeout: float = 5.0) -> bool:
        try:
            response = requests.head(self.url, timeout=timeout)
            return True if response.status_code == 200 else False
        except requests.exceptions.RequestException:
            return False


class M3U8Stream(IPTVStream):
    STREAMTYPE: str = "M3U8"

    def __init__(self, channel: IPTVChannel):
        self.__transport: Optional[M3U8] = None
        super().__init__(channel)

    @property
    def transport(self) -> M3U8:
        if self.__transport is None:
            self.__transport = load(uri=self.url)
        return self.__transport


class MPDStream(IPTVStream):
    STREAMTYPE: str = "MPD"

    def __init__(self, channel: IPTVChannel):
        super().__init__(channel)


STREAM = Union[M3U8Stream, MPDStream]


def load_stream(channel: IPTVChannel) -> STREAM:
    file_type: str = os.path.splitext(channel.url)[1].lower()
    return {
        ".mpd": MPDStream,
        ".m3u8": M3U8Stream,
    }[file_type](channel)
