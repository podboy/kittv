# coding:utf-8

from queue import Empty
from queue import Queue
from typing import List
from typing import Optional

from xkits import TaskPool

from .stream import IPTVStream
from .tuning import Tunes


class PlaylistTask(TaskPool):
    def __init__(self, probe: bool = False, filter: bool = False):
        super().__init__(workers=1, prefix="merge_task")
        self.__streams: Queue[IPTVStream] = Queue()
        self.__playlists: Tunes = Tunes()
        self.__check: bool = probe or filter
        self.__probe: bool = probe
        self.__filter: bool = filter

    def __enter__(self):
        self.submit(self.__merge_task)
        super().__enter__()
        return self

    @property
    def streams(self) -> Queue[IPTVStream]:
        return self.__streams

    @property
    def check(self) -> bool:
        return self.__check

    @property
    def probe(self) -> bool:
        return self.__probe

    @property
    def filter(self) -> bool:
        return self.__filter

    @property
    def playlists(self) -> Tunes:
        return self.__playlists

    def __merge_task(self):
        '''merge streams into new playlist'''
        while True:
            try:
                stream: IPTVStream = self.streams.get(timeout=0.01)
                items: List[str] = [stream.name, stream.url]
                if self.probe:
                    items.append("good" if stream.available else "bad")
                self.cmds.stdout(", ".join(items))
                self.playlists.append(stream)
            except Empty:
                if not self.running:
                    break

    def __check_task(self, stream: IPTVStream):
        '''check stream availability'''
        if not self.check or stream.available or not self.filter:
            self.streams.put(stream, block=True)

    def save(self, path: str) -> bool:
        '''save playlist to file'''
        return self.playlists.dumpfile(path)

    def list(self, playlists: List[str], workers: int = 64,
             output: Optional[str] = None):
        with TaskPool(workers=workers, prefix="check_task") as checker:
            for playlist in playlists:
                tune = Tunes.load(playlist)
                for stream in tune.streams:
                    checker.submit(self.__check_task, stream)
        self.barrier()
        if output:
            self.save(output)
