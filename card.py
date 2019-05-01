"""
These class use a lot of crappy Cribbage assumptions
None of them will work for non-Cribbage card games
TODO: Everything is too slow, fasten it up
"""
import math
from collections import deque, Counter

from itertools import combinations

from util import powerset_min_len

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

    def serialize(self) -> int:  # Gives the numeric
        return self.SUITS.index(self.suit) * 13 + self.RANKS.index(self.rank)

    @classmethod
    def deserialize(cls, num):
        assert 0 <= num < 51
        rank = cls.RANKS[num % 13]
        suit = cls.SUITS[num // 13]
        return cls(rank, suit)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.rank}, {self.suit})"

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

    @property
    def remaining_cards(self):
        return self.cards[self.top:]

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
        self.cards = list(cards)

    @property
    def is_empty(self):
        return len(self) == 0

    def add(self, card):
        self.cards.append(card)

    def pop(self, card):
        self.cards.remove(card)
        return card

    def count(self, cut_card=None):
        assert len(self.cards) == 4

        cards = self.cards[:]
        cards.append(cut_card)

        rank_counter = Counter(card.rank for card in cards)
        suit_counter = Counter(card.suit for card in self.cards)

        total = 0
        # 15s
        for combo in powerset_min_len(cards):
            if sum(card.value for card in combo) == 15:
                total += 2

        # Pairs
        for _, num in rank_counter.most_common():
            if num == 1:
                break
            else:
                total += {2: 2, 3: 6, 4: 12}[num]

        # Flush
        if len(suit_counter) == 1:
            total += 4
            if cut_card.suit in suit_counter.keys():
                total += 1

        # Runs
        num_in_a_row = 0
        multiplier = 1
        for rank in CribbageCard.RANKS:
            if rank in rank_counter:
                num_in_a_row += 1
                multiplier *= rank_counter[rank]
            else:
                if num_in_a_row >= 3:
                    points = (num_in_a_row * multiplier)
                    total += points
                num_in_a_row = 0
                multiplier = 1

        # Knobs
        jack_suits = [card.suit for card in self.cards if card.rank == 'Jack']
        if cut_card.suit in jack_suits:
            total += 1

        return total

    def predict(self, remaining_cards: list, quality: float = 1.0):
        """
        Uses statistical analysis to assign a number value to these cards
        denoting their point value. The higher quality is, the longer a
        prediction takes to complete
        """
        orig_cards = self.cards

        assert len(self.cards) <= 4
        assert 0 < quality <= 1.0

        remaining_cards = remaining_cards[:math.ceil(len(remaining_cards) * quality)]

        num = 0
        total_count = 0

        for fillup in combinations(remaining_cards, 4 - len(self.cards)):
            self.cards = orig_cards + list(fillup)
            rest = remaining_cards[:]
            for card in fillup:
                rest.remove(card)
            for cut_card in rest:
                num += 1
                count = self.count(cut_card)
                total_count += count

        return total_count / num

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
