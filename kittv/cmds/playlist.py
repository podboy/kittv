# coding:utf-8

from typing import List
from typing import Optional

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ..utils import PlaylistTask


@add_command("playlist", help="list streams")
def add_cmd_playlist(_arg: argp):
    marg = _arg.add_mutually_exclusive_group()
    marg.add_argument("--probe", help="probe stream availability", action="store_true")  # noqa:E501
    marg.add_argument("--filter", help="filter out bad streams", action="store_true")  # noqa:E501
    _arg.add_argument("-o", "--output", type=str, help="output playlist",
                      nargs="?", const="playlist.m3u", default=None,
                      metavar="FILE")
    _arg.add_argument("--workers", type=int, help="maximum task threads",
                      nargs="?", const=8, default=1, metavar="NUM")
    _arg.add_argument(dest="playlists", help="m3u format file or url",
                      type=str, nargs="+", metavar="PLAYLIST")


@run_command(add_cmd_playlist)
def run_cmd_playlist(cmds: commands) -> int:
    probe: bool = cmds.args.probe
    filter: bool = cmds.args.filter
    with PlaylistTask(probe=probe, filter=filter) as tasker:
        workers: int = cmds.args.workers or 1
        output: Optional[str] = cmds.args.output
        playlists: List[str] = cmds.args.playlists
        tasker.list(playlists=playlists, workers=workers, output=output)
    return 0
