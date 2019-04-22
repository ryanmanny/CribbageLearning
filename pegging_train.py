"""
https://adventuresinmachinelearning.com/reinforcement-learning-tensorflow/
"""
from game import CribbageGame, RoboCribbagePlayer


def peg(self: RoboCribbagePlayer):
    """
    Uses reinforcement learning to choose pegging card
    """
    game = self._game
    pegging_pile = game.pegging_pile
    is_dealer = game.dealer == self

    raise NotImplementedError


class PeggingTestGame(CribbageGame):
    def turn(self):
        """
        Simulates pegging over and over
        Supposedly Reinforces Learning
        """
        self._deck.shuffle()

        self._make_players_peg()

        self._change_dealer()

    def play(self):
        while True:
            self.turn()


def main():
    player1 = RoboCribbagePlayer(1)
    player1.put_down_pegging_card = peg

    player2 = RoboCribbagePlayer(2)
    player2.put_down_pegging_card = peg

    players = [
        player1,
        player2,
    ]
    CribbageGame(players).play()


if __name__ == '__main__':
    main()
