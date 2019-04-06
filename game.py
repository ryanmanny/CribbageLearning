"""
You may notice a general sense of hackiness throughout the game logic.
The intent of this project is to create a good interface to a Cribbage AI that
could be hooked into any Cribbage game. Because of this, this cribbage game
will not be very fun
"""

import random
import itertools

from card import CribbageDeck, CribbageHand, CribbagePeggingPile

HAND_SIZE = 4


class CribbagePlayer:
    def __init__(self):
        self._game = None

        self._hand = None
        self._pegging_hand = None
        self._points = 0

    def throw_away_cards(self):
        num_to_throw = len(self._hand) - HAND_SIZE

        while True:
            print(f"{self.hand!s}")
            indexes = input(
                f"Enter the indexes ({num_to_throw}) you want to throw away: "
            ).split()
            if len(indexes) != num_to_throw:
                print("Not the right number to throw away")
                continue
            for index in indexes:
                try:
                    index = int(index)
                except ValueError:
                    print(f"{index} cannot be converted to int")
                    continue
                try:
                    card = self.hand[index]
                except IndexError:
                    print(f"{index} is not a valid index")
                    continue

                # Move cards to crib
                self.hand.pop(card)
                self._game.crib.add(card)
            break

    def put_down_pegging_card(self):
        pegging_pile = self._game.pegging_pile

        while True:
            print(f"Pegging pile count: {pegging_pile.count()}")
            print(f"PILE = {pegging_pile!s}")
            print(f"{self.pegging_hand!s}")

            try:
                index = int(input(
                    f"Enter the index of the card you want to put down: "
                ))
            except ValueError:
                print("Invalid")
                continue

            card = self.hand[index]

            if pegging_pile.count() + card.value > pegging_pile.PEGGING_LIMIT:
                print(f"Pegging pile cannot exceed {pegging_pile.PEGGING_LIMIT}")
                continue
            else:
                self.hand.pop(card)
                self.points += pegging_pile.add(card)
            break

    @property
    def minimum_card(self):
        """
        Used to check if a player must say GO
        """
        return min(card.value for card in self.hand)

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


class RoboCribbagePlayer(CribbagePlayer):
    def throw_away_cards(self):
        raise NotImplementedError

    def put_down_pegging_card(self):
        raise NotImplementedError


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

    def _change_dealer(self):
        self._dealer = next(self._dealer_iter)

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
        if cut_card.rank == 'Jack':
            self.dealer.points += 2

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

        while not all(player.hand.is_empty for player in self._players):
            for player in self._players:
                if go:  # This player plays until she can't go either
                    player.points += 1  # One point for Go
                    while True:
                        go = player.put_down_pegging_card(self._pegging_pile)
                        if go:
                            self._pegging_pile.reset()  # Neither player can play
                            break
                        last_player = player
                elif not player.hand.is_empty:
                    go = player.put_down_pegging_card(self._pegging_pile)
                    last_player = player

        last_player.points += 1  # One for last card
        self._pegging_pile.reset()

    def _count_players_hands(self):
        """
        Abstracts the counting away from the player, it's not very important
        Automatically adds points in the hand to score
        """
        for player in self._players:
            player.points += player.hand.count(self._cut_card)

    def _count_crib(self):
        self.dealer.points += self._crib.count(self._cut_card)

    def turn(self):
        """
        Does all logic necessary for a turn of Cribbage to take place
        """
        self._deck.shuffle()

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

        input("Game is over")


if __name__ == '__main__':
    players = [
        CribbagePlayer(),
        CribbagePlayer(),
    ]
    CribbageGame(players).play()
