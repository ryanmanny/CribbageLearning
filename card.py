"""
These class use a lot of crappy Cribbage assumptions
None of them will work for non-Cribbage card games
"""
from collections import deque

import random


class CribbageCard:
    RANKS = [
        'Ace',
        'Two',
        'Three',
        'Four',
        'Five',
        'Six',
        'Seven',
        'Eight',
        'Nine',
        'Ten',
        'Jack',
        'Queen',
        'King',
    ]

    SUITS = [
        'Spades',
        'Hearts',
        'Clubs',
        'Diamonds',
    ]

    RANK_TO_VAL = {
        # Ideally pass as a param to a CardClassFactory or something
        'Ace': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5,
        'Six': 6,
        'Seven': 7,
        'Eight': 8,
        'Nine': 9,
        'Ten': 10,
        'Jack': 10,
        'Queen': 10,
        'King': 10,
    }

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    @property
    def value(self):
        return self.RANK_TO_VAL[self.rank]

    @classmethod
    def all(cls):
        return [
            cls(rank, suit)
            for rank in cls.RANKS
            for suit in cls.SUITS
        ]

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class CribbageDeck:
    def __init__(self):
        self.card_cls = CribbageCard

        self.top = 0
        self.cards = self.card_cls.all()

    def shuffle(self):
        self.top = 0
        random.shuffle(self.cards)

    def draw(self):
        try:
            card = self.cards[self.top]
        except IndexError:
            raise ValueError("Out of cards!")

        self.top += 1
        return card

    def deal(self, num_cards):
        return [self.draw() for _ in range(num_cards)]


class CribbageHand:
    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self.cards = cards

    @property
    def is_empty(self):
        return len(self) == 0

    def add(self, card):
        self.cards.append(card)

    def pop(self, card):
        self.cards.remove(card)
        return card

    def count(self, cut_card=None):
        raise NotImplementedError

    def __getitem__(self, index) -> CribbageCard:
        return self.cards[index - 1]

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return "\n".join(f"{i}. {card}" for i, card in enumerate(self.cards, 1))


class CribbagePeggingPile:
    PEGGING_LIMIT = 31

    def __init__(self):
        self.cards = deque()

    def _scored_points(self):
        """
        Return the number of points the top card would score
        """
        points = 0

        num_cards = len(self)
        count = self.count()

        # FIND 15 and 31 POINTS
        if count == 15:
            print("15 for 2")
            points += 2
        elif count == 31:
            print("31 for 2")
            points += 2

        # FIND SEQUENCE POINTS
        for i in range(3, num_cards + 1):
            card_ranks = [
                # TODO: Find a good way to refactor this
                CribbageCard.RANKS.index(card.rank)
                for card in list(self)[num_cards - i::]
            ]
            print(f"CARD RANKS {card_ranks}")

        return points

    def reset(self):
        self.cards = deque()

    def add(self, card):
        self.cards.append(card)
        return self._scored_points()

    def count(self):
        return sum(card.value for card in self.cards)

    def min_required(self):
        return self.PEGGING_LIMIT - self.count()

    def __getitem__(self, index):
        return self.cards[index]

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"{list(str(card) for card in self.cards)}"
