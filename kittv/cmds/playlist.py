# coding:utf-8

from typing import List

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils.tuning import Tunes


def add_pos_playlist(_arg: argp):
    _arg.add_argument(dest="playlists", help="m3u format file or url",
                      type=str, nargs="+", metavar="PLAYLIST")


@add_command("list", help="list playlist")
def add_cmd_playlist_list(_arg: argp):
    add_pos_playlist(_arg)


@run_command(add_cmd_playlist_list)
def run_cmd_playlist_list(cmds: commands) -> int:
    playlists: List[str] = cmds.args.playlists
    for playlist in playlists:
        tune = Tunes.load(playlist)
        for ch in tune:
            cmds.stdout(f"{ch.tvg_id}")
            for s in tune[ch.tvg_id]:
                cmds.stdout(f"└─{s.name}, {s.url}")
    return 0


@add_command("playlist")
def add_cmd_playlist(_arg: argp):
    pass


@run_command(add_cmd_playlist, add_cmd_playlist_list)
def run_cmd_playlist(cmds: commands) -> int:
    return 0
