"""

"""

import asyncio
import sys
import select
import json


class CommandOpcodes():
    LOBBY_MAKE = b"\x00"
    LOBBY_ADD = b"\x01"
    LOBBY_REMOVE = b"\x02"
    GAME_REMOVE = b"\x03"
    GAME_CMD = b"\x04"


class ConfirmOpcodes():
    LOBBY_MADE = b"\x00"
    LOBBY_ADDED = b"\x01"
    LOBBY_REMOVED = b"\x02"
    GAME_REMOVED = b"\x03"
    GAME_CMD = b"\x04"
    GAME_END = b"\x05"

async def read_msg(stream=sys.stdin.buffer):
    async def read(length):
        res = []
        while len(res) < length:
            await asyncio.sleep(0)
            if not select.select([stream], [], [], 0)[0]:
                continue
            res.extend(stream.read1(length - len(res)))
        return bytes(res)

    async def read_num():
        size = 1
        while True:
            num = int.from_bytes(await read(size), "little")
            if num != (1 << (8 * size)) - 1:
                return num

    return [await read(await read_num())
            for count in range(await read_num())]


def write_msg(args, stream=sys.stdout.buffer):
    def write_num(num):
        size = (num + 1).bit_length()
        curr_size = 1
        while curr_size * 8 < size:
            stream.write(b"\xff" * curr_size)
        stream.write(num.to_bytes(curr_size, "little"))

    write_num(len(args))
    for arg in args:
        write_num(len(arg))
        stream.write(arg)
    stream.flush()


def make_base_lobby(game):
    class Lobby():
        def __init__(self):
            self.players = set()

        def add_player(self, id_):
            self.players.add(id_)
            return len(self.players) == 2

        def remove_player(self, id_):
            self.players.remove(id_)
            return len(self.players) == 0

        def make_game(self):
            return game(self.players)

    return Lobby


class MessageRouter():
    def __init__(self, lobby, json=True, handlers=None):
        self.lobbies = {}
        self.games = {}

        self.handlers = {
            CommandOpcodes.LOBBY_MAKE: self.handle_lobby_make,
            CommandOpcodes.LOBBY_ADD: self.handle_lobby_add,
            CommandOpcodes.LOBBY_REMOVE: self.handle_lobby_remove,

            CommandOpcodes.GAME_REMOVE: self.handle_game_remove,
            CommandOpcodes.GAME_CMD: self.handle_game_cmd,
        }
        self.handlers.update(handlers or {})

        self.lobby = lobby
        self.json = json

    def make_senders(self, name):
        # arguably bad practice, but looks nice IMO
        def send(to, data):
            data = json.dumps(data).encode()
            write_msg([ConfirmOpcodes.GAME_CMD, name, to, data])

        def send_text(to, data):
            data = data.encode()
            write_msg([ConfirmOpcodes.GAME_CMD, name, to, data])
        send.text = send_text

        def send_bytes(to, data):
            write_msg([ConfirmOpcodes.GAME_CMD, name, to, data])
        send.bytes = send_bytes

        return send

    async def run_game(self, name, game):
        send = self.make_senders(name)
        await game.run(send)
        del self.games[name]

    async def handle_lobby_make(self, name):
        self.lobbies[name] = self.lobby()
        write_msg([ConfirmOpcodes.LOBBY_MADE, name])

    async def handle_lobby_add(self, name, id_):
        full = self.lobbies[name].add_player(id_)

        if full:
            game = self.lobbies[name].make_game()
            del self.lobbies[name]

            handler = asyncio.Task(self.run_game(name, game))
            asyncio.ensure_future(handler)
            self.games[name] = (game, handler)

            write_msg([ConfirmOpcodes.LOBBY_ADDED, name, id_, b"\x01"])

        else:
            write_msg([ConfirmOpcodes.LOBBY_ADDED, name, id_, b"\x00"])

    async def handle_lobby_remove(self, name, id_):
        if self.lobbies[name].remove_player(id_):
            del self.lobbies[name]
        write_msg([ConfirmOpcodes.LOBBY_REMOVED, name, id_])

    async def handle_game_remove(self, name, id_):
        game, handler = self.games[name]
        if game.remove_player(id_):
            handler.cancel()
            del self.games[name]
        write_msg([ConfirmOpcodes.GAME_REMOVED, name, id_])

    async def handle_game_cmd(self, name, from_, data):
        game, _ = self.games[name]
        game.handle_cmd(from_, data)

    async def handle_cmd(self, cmd, *data):
        if cmd in self.handlers:
            await self.handlers[cmd](*data)

    async def run(self):
        while True:
            await self.handle_cmd(*await read_msg())


def run(lobby, **kw):
    router = MessageRouter(lobby, **kw)
    asyncio.get_event_loop().run_until_complete(router.run())
