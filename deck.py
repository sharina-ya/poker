import random
from enum import Enum
import hashlib
import random
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


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
        self.id = 0

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


class Dealer:
    def __init__(self):
        self.cards = []
        private_key, public_key = self.generate_key_pair()

        self.private_key = private_key
        self.public_key = public_key

        print(f"Приватный ключ дилера:", self.private_key)
        print(f"Публичный ключ дилера:", self.public_key)

        self.players_public_keys = []

    def generate_key_pair(self):
        print("Создаются ключи для дилера...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        return private_key, public_key

    def digital_sign(self, data):
        return self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def initial_shuffle(self):
        self.cards = []

        print("Дилер создает колоду...")
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(rank, suit))

        for i in range(len(self.cards)):
            self.cards[i].id = str(i)

        self.shuffle()

    def shuffle(self):
        """Перемешать колоду"""
        print("Дилер тасует колоду...")
        random.shuffle(self.cards)

    def get_card_for_player(self, player_public_key):
        """Взять карту из колоды"""
        if len(self.cards) > 0:
            card = self.cards.pop()
            card.visible = True

            R_1 = os.urandom(8).hex()
            print('Дилер шифрует карту ', card.rank, card.suit)

            sign_data = R_1.encode() + card.id.encode()
            print("Дилер подписывает карту")
            signature = self.digital_sign(sign_data)

            data = {
                'card': card.id,
                'salt': R_1,
            }

            byte_data = json.dumps(data).encode()

            card_enc = player_public_key.encrypt(
                byte_data,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                             algorithm=hashes.SHA256(),
                             label=None)
            )

            return card_enc, signature

        else:
            print("Deck is empty")
            return None

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