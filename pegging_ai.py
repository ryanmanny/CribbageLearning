"""
https://adventuresinmachinelearning.com/reinforcement-learning-tensorflow/
"""
import random
from game import CribbageGame, RoboCribbagePlayer

try:
    from rl_ai import AIPeg
except ImportError:
    # raise EnvironmentError("Reid hasn't written this yet")
    def AIPeg(cards, pegging_count, top_card):
        print(f"cards {cards}")
        print(f"pegging count {pegging_count}")
        print(f"top card {top_card}")
        return random.randint(0, len(cards) - 1)


class RoboCribbagePeggerPlayer(RoboCribbagePlayer):
    def put_down_pegging_card(self):
        """
        Uses reinforcement learning to choose pegging card
        """
        game = self._game
        pegging_pile = game.pegging_pile

        if len(self.pegging_hand) == 0 or \
                pegging_pile.count() + self.minimum_card > pegging_pile.PEGGING_LIMIT:
            print(f"{self} says GO")
            return True

        try:
            top_card = pegging_pile.cards[-1].serialize() % 13
        except IndexError:
            top_card = None

        index = AIPeg(
            [card.serialize() % 13 for card in self.pegging_hand],
            pegging_pile.count(),
            top_card,
        )

        card = self.pegging_hand[index + 1]

        while pegging_pile.count() + card.value > pegging_pile.PEGGING_LIMIT:
            index = random.randint(0, len(self.pegging_hand) - 1)
            card = self.pegging_hand[index + 1]

        self.pegging_hand.pop(card)
        self.points += pegging_pile.add(card)

        return False


class PeggingTestGame(CribbageGame):
    def turn(self):
        """
        Simulates pegging over and over
        Supposedly Reinforces Learning
        """
        self._deck.shuffle()
        self._deal()

        self._make_players_peg()

        self._change_dealer()

    def play(self):
        try:
            while True:
                self.turn()
        except self.GameOver:
            self._print_scores()


def main():
    PeggingTestGame([
        RoboCribbagePeggerPlayer(1),
        RoboCribbagePlayer(2),
    ]).play()


if __name__ == '__main__':
    main()
