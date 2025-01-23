# coding:utf-8

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command

from ..utils import StreamProber


@add_command("probe", help="probe stream availability")
def add_cmd_probe(_arg: argp):
    _arg.add_argument("--timeout", help="default is 3 seconds",
                      type=int, nargs=1, default=[3], metavar="SEC")
    _arg.add_argument(dest="stream_url", help="stream url",
                      type=str, nargs=1, metavar="URL")


@run_command(add_cmd_probe)
def run_cmd_probe(cmds: commands) -> int:
    try:
        url: str = cmds.args.stream_url[0]
        timeout: float = float(cmds.args.timeout[0])
        prober: StreamProber = StreamProber.ffprobe(url=url, timeout=timeout)
        probe_score: int = prober.format.probe_score
        cmds.stdout(f"score: {probe_score}")
    except Exception:
        cmds.stdout("score: -1")
    return 0
