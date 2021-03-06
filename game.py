"""
You may notice a general sense of hackiness throughout the game logic.
The intent of this project is to create a good interface to a Cribbage AI that
could be hooked into any Cribbage game. Because of this, this cribbage game
will not be very fun
"""

import random
import itertools
import copy

from card import CribbageDeck, CribbageHand, CribbagePeggingPile
from throwing_ai import ThrowingClassifier, RandomThrowingClassifier

HAND_SIZE = 4


class CribbagePlayer:
    def __init__(self, player_num):
        self.player_num = player_num
        self._game = None

        self._hand = None
        self._pegging_hand = None
        self._points = 0

    def throw_away_cards(self):
        num_to_throw = len(self._hand) - HAND_SIZE

        while True:
            print("***YOUR CARDS***")
            print(f"{self.hand!s}")
            indexes = input(
                f"Enter the indexes ({num_to_throw}) you want to throw away: "
            ).split()

            # Check that there are the right number of indexes
            if len(indexes) != num_to_throw:
                print("Not the right number to throw away")
                continue

            # Check that indexes are actually integers
            try:
                indexes = [int(index) for index in indexes]
            except ValueError as e:
                print(f"{e.args} cannot be converted to int")
                continue

            # Check that indexes aren't out of bounds
            try:
                cards = [self.hand[index] for index in indexes]
            except IndexError as e:
                print(f"{e.args} is not a valid index")
                continue

            # Move cards to crib
            for card in cards:
                self.hand.pop(card)
                self._game.crib.add(card)
                self._pegging_hand = copy.deepcopy(self.hand)
            break

    def put_down_pegging_card(self) -> bool:
        """
        Returns True if player has to say GO
        """
        print(f"{self}'s turn")

        pegging_pile = self._game.pegging_pile

        # Check if Player has to say GO
        if len(self.pegging_hand) == 0 or \
                pegging_pile.count() + self.minimum_card > pegging_pile.PEGGING_LIMIT:
            print(f"{self} says GO")
            return True

        while True:
            print(f"Pegging pile count: {pegging_pile.count()}")
            print(f"***PILE**")
            print(f"{pegging_pile!s}")
            print(f"***CARDS YOU HAVE LEFT***")
            print(f"{self.pegging_hand!s}")

            try:
                index = int(input(
                    f"Enter the index of the card you want to put down: "
                ))
            except ValueError:
                print("Invalid")
                continue

            card = self.pegging_hand[index]

            if pegging_pile.count() + card.value > pegging_pile.PEGGING_LIMIT:
                print(f"Pegging pile cannot exceed {pegging_pile.PEGGING_LIMIT}")
                continue
            else:
                self.pegging_hand.pop(card)
                self.points += pegging_pile.add(card)
            break

        return False

    @property
    def minimum_card(self):
        """
        Used to check if a player must say GO
        """
        try:
            return min(card.value for card in self.pegging_hand)
        except ValueError:  # Empty sequence
            # TODO: Figure out something good to do here
            raise

    @property
    def hand(self) -> CribbageHand:
        return self._hand

    @hand.setter
    def hand(self, new_hand):
        """
        Sets both hand variables at the same time, since they are both
        handled independently (this is a hack!)
        """
        self._hand = CribbageHand(new_hand)
        self._pegging_hand = CribbageHand(new_hand)

    @property
    def pegging_hand(self) -> CribbageHand:
        """
        Set using self.hand
        """
        return self._pegging_hand

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        """
        A hacky event handler. Why does the game ask the player if he won?
        """
        self._points = value
        if self._points > 120:
            self._game.win_handler(self)

    def __str__(self):
        return f"Player {self.player_num}"


class RoboCribbagePlayer(CribbagePlayer):
    def __init__(self, *args, **kwargs):
        self.throwing_classifier = ThrowingClassifier.load()

        super().__init__(*args, **kwargs)

    def throw_away_cards(self):
        game = self._game
        is_dealer = self is game.dealer
        hand = self.hand

        assert len(hand) == 6

        serialized_cards = [card.serialize() for card in hand]

        indexes = self.throwing_classifier.throw(is_dealer, serialized_cards)

        # Check that indexes aren't out of bounds
        try:
            cards = [self.hand[index] for index in indexes]
        except IndexError as e:
            raise ValueError("The AI is broken")

        # Move cards to crib
        for card in cards:
            hand.pop(card)
            game.crib.add(card)

        self._pegging_hand = copy.deepcopy(self.hand)

        print(f"***AI PLAYER {self.player_num} HAS THROWN AWAY***")

    def put_down_pegging_card(self):
        """
        Chooses a random card to throw away
        """
        pegging_pile = self._game.pegging_pile

        if len(self.pegging_hand) == 0 or \
                pegging_pile.count() + self.minimum_card > pegging_pile.PEGGING_LIMIT:
            print(f"{self} says GO")
            return True

        while True:
            index = random.randint(0, len(self.pegging_hand) - 1)

            card = self.pegging_hand[index + 1]

            if pegging_pile.count() + card.value > pegging_pile.PEGGING_LIMIT:
                continue
            else:
                self.pegging_hand.pop(card)
                self.points += pegging_pile.add(card)
            break

        return False


class CribbageGame:
    class GameOver(StopIteration):
        """
        Has science gone too far?
        """

    def __init__(self, players):
        if len(players) != 2:
            raise NotImplementedError("Only two players allowed")
        self._players = players
        for player in self._players:
            player._game = self  # Used so AI can query things it needs to

        self._dealer_iter = itertools.cycle(self._players)
        for i in range(random.randint(0, len(self._players) - 1)):
            next(self._dealer_iter)  # Randomly initializes dealer cycle
        self._dealer = next(self._dealer_iter)

        self._crib = CribbageHand()

        self._deck = CribbageDeck()
        self._pegging_pile = CribbagePeggingPile()
        self._cut_card = None

    @property
    def dealer(self):
        return self._dealer

    @property
    def players(self):
        return self._players

    @property
    def crib(self) -> CribbageHand:
        return self._crib

    @property
    def pegging_pile(self) -> CribbagePeggingPile:
        return self._pegging_pile

    def _print_scores(self):
        for player in self.players:
            print(f"***{player!s} has {player.points} points***")

    def _change_dealer(self):
        self._dealer = next(self._dealer_iter)
        self._crib = CribbageHand()  # Reset crib

    def win_handler(self, player):
        assert player.points > 120, ValueError("You little scumbag")
        print(f"{player!s} has winned")
        raise self.GameOver

    def _deal(self):
        for player in self._players:
            player.hand = self._deck.deal(6)

    def _cut(self):
        """
        Automatically cuts, since there is no strategy worth exploring there
        """
        cut_card = self._deck.draw()
        print(f"***CUT CARD IS {cut_card!s}***")
        if cut_card.rank == 'Jack':
            self.dealer.points += 2

        self._cut_card = cut_card

    def _make_players_throw_away(self):
        """
        Asks players which cards to throw away
        """
        for player in self._players:
            player.throw_away_cards()

    def _make_players_peg(self):
        """
        Performs the pegging process, asking users for input when necessary
        """
        go = False
        last_player = None

        pegging_pile = self._pegging_pile

        round = 0

        while not all(player.pegging_hand.is_empty for player in self._players):
            if pegging_pile.count() == 31:
                last_player.points += 2
                pegging_pile.reset()
                continue

            for player in self._players:
                if round == 0 and player is self.dealer:
                    continue  # The opponent starts

                round += 1

                if go:  # This player plays until she can't go either
                    player.points += 1  # One point for Go
                    while True:
                        go = player.put_down_pegging_card()
                        if go:
                            pegging_pile.reset()  # Neither player can play
                            break
                        last_player = player
                elif not player.hand.is_empty:
                    go = player.put_down_pegging_card()
                    last_player = player
                else:
                    break

        last_player.points += 1  # One for last card
        pegging_pile.reset()

    def _count_players_hands(self):
        """
        Abstracts the counting away from the player, it's not very important
        Automatically adds points in the hand to score
        """
        for player in self._players:
            print(f"***{player!s} has these cards***")
            print(f"{player.hand!s}")
            print(f"Cut Card: {self._cut_card}")
            points = player.hand.count(self._cut_card)
            print(f"***They were worth {points} points")
            player.points += points

    def _count_crib(self):
        print(f"***{self.dealer!s} has the crib***")
        print(f"{self._crib!s}")
        print(f"Cut Card: {self._cut_card}")
        points = self._crib.count(self._cut_card)
        print(f"***They were worth {points} points")
        self.dealer.points += points

    def turn(self):
        """
        Does all logic necessary for a turn of Cribbage to take place
        """
        self._print_scores()
        print(f"***{self.dealer!s} is the dealer***")

        print("***Shuffling Deck***")
        self._deck.shuffle()

        print("***Dealing Cards***")
        self._deal()
        self._make_players_throw_away()

        self._cut()
        self._make_players_peg()

        self._count_players_hands()
        self._count_crib()

        self._change_dealer()

    def play(self):
        while True:
            try:
                self.turn()
            except self.GameOver:
                break

        self._print_scores()

        input("Game is over")


def main():
    players = [
        CribbagePlayer(1),
        RoboCribbagePlayer(2),
    ]
    CribbageGame(players).play()


if __name__ == '__main__':
    main()
