# might replace with node.js if we need to

import subprocess
import asyncio

from games.python.lib import CommandOpcodes, ConfirmOpcodes, read_msg, write_msg

GAMES = {
    "rps": ["python3", "carnival/games/python/rps.py"],
}


class Game(subprocess.Popen):
    def __init__(self, cmd):
        super().__init__(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def write_msg(self, args):
        write_msg(args, self.stdin)

    async def read_msg(self):
        return await read_msg(self.stdout)


async def print_messages(game):
    while True:
        print(await game.read_msg())


async def main():
    g = Game(GAMES["rps"])
    asyncio.ensure_future(print_messages(g))

    g.write_msg([b"\x00", b"abc"])
    g.write_msg([b"\x01", b"abc", b"1"])
    g.write_msg([b"\x01", b"abc", b"2"])
    g.write_msg([b"\x04", b"abc", b"1", b"2"])
    g.write_msg([b"\x04", b"abc", b"2", b"0"])
    await asyncio.sleep(5)

asyncio.get_event_loop().run_until_complete(main())
