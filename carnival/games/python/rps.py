"""
this was tic tac toe
replacing it with rock-paper-scissors for now since its simpler
"""

import asyncio

import lib


class Game():
    def __init__(self, players):
        self.players = players
        self.played = {}
    
        self.all_played = asyncio.Event()

    def remove_player(self, player):
        self.players.remove(player)
        self.played.pop(player, None)
        if len(self.played) >= len(self.players):
            self.all_played.set()

    def handle_cmd(self, player, played):
        # setdefault so they cant change it
        self.played.setdefault(player, int(played))
        if len(self.played) == len(self.players):
            self.all_played.set()

    async def run(self, send):
        await self.all_played.wait()

        if len(self.players) == 2:
            player_1, player_2 = [self.players.pop() for _ in range(2)]
            played_1, played_2 = self.played[player_1], self.played[player_2]
            diff = (played_1 - played_2) % 3

            if diff == 0:
                send.text(player_1, "Tied")
                send.text(player_2, "Tied")

            elif diff == 1:
                send.text(player_1, "Win")
                send.text(player_2, "Lose")

            elif diff == 2:
                send.text(player_1, "Lose")
                send.text(player_2, "Win")

        else:  # if someone left
            # might lose a player while sending, copy as a tuple
            for player in tuple(self.players):
                send.text(player, "no winner, someone left")


lib.run(lobby=lib.make_base_lobby(Game))
