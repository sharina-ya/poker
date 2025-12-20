import random
from enum import Enum


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @property
    def value_int(self):
        """Числовое значение карты"""
        values = {
            Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5,
            Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9,
            Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12,
            Rank.KING: 13, Rank.ACE: 14
        }
        return values[self]

    @property
    def symbol(self):
        """Символ карты"""
        return self.value


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.visible = False
        self.x = 0
        self.y = 0

    def __str__(self):
        if self.visible:
            return f"{self.rank.value}{self.suit.value}"
        return "XX"

    def __repr__(self):
        return str(self)

    @property
    def value(self):
        """Числовое значение карты"""
        return self.rank.value_int

    def get_color(self):
        """Цвет карты (красный для червей и бубей)"""
        if self.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            return (200, 0, 0)
        return (0, 0, 0)


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        """Создать новую колоду и перемешать"""
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(rank, suit))
        self.shuffle()

    def shuffle(self):
        """Перемешать колоду"""
        random.shuffle(self.cards)

    def draw(self):
        """Взять карту из колоды"""
        if len(self.cards) > 0:
            card = self.cards.pop()
            card.visible = True
            return card
        return None

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck with {len(self.cards)} cards"