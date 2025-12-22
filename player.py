from deck import Card, Suit, Rank
import hashlib
import random
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

types_of_cards = []
i = 0
for suit in Suit:
    for rank in Rank:
        types_of_cards.append(Card(rank, suit))
        types_of_cards[-1].id = i
        i += 1

class Player:
    def __init__(self, name, position, chips=1000):
        self.name = name
        self.position = position
        self.hand = []
        self.chips = chips
        self.bet = 0
        self.total_bet = 0
        self.folded = False
        self.all_in = False
        self.is_active = True
        self.is_turn = False
        self.show_cards = False

        private_key, public_key = self.generate_key_pair()

        self.private_key = private_key
        self.public_key = public_key

        print(f"Приватный ключ игрока {self.name}:", self.private_key)
        print(f"Публичный ключ игрока {self.name}:", self.public_key)

        self.dealer_public_key = None

    def generate_key_pair(self):
        print(f"Создаются ключи для {self.name}...")

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        return private_key, public_key

    def verify_sign(self, signature, data):
        try:
            self.dealer_public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except Exception:
            return False

    def decrypt_card(self, data_enc, signature):
        print(f"{self.name} расшифровывает карту...")
        plaintext = self.private_key.decrypt(
            data_enc,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                         algorithm=hashes.SHA256(),
                         label=None)
        )
        data_dec = json.loads(plaintext.decode('utf-8'))

        card_id = data_dec['card']
        salt = data_dec['salt']

        print(f"{self.name} проверяет подлинность подписи...")

        verify_data = salt.encode() + card_id.encode()
        is_valid = self.verify_sign(signature, verify_data)

        if not is_valid:
            print("Цифровая подпись некорректна")
        else:
            print("Цифровая подпись подтверждена")
            self.add_card(types_of_cards[int(card_id)])
            print(f"{self.name} получает карту", self.hand[-1].rank, self.hand[-1].suit)

    def reset_hand(self):
        """Сбросить руку и состояние для нового раунда"""
        self.hand = []
        self.bet = 0
        self.total_bet = 0
        self.folded = False
        self.all_in = False
        self.is_active = True
        self.show_cards = False

    def add_card(self, card):
        """Добавить карту в руку"""
        if len(self.hand) < 2:
            self.hand.append(card)
            return True
        return False

    def can_bet(self, amount):
        """Проверить, может ли игрок сделать ставку"""
        if self.folded:
            return False
        if amount > self.chips:
            return False
        return True

    def make_bet(self, amount):
        """Сделать ставку"""
        if not self.can_bet(amount):
            return False

        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.bet = actual_bet
        self.total_bet += actual_bet

        if self.chips == 0:
            self.all_in = True

        return True

    def fold(self):
        """Сбросить карты"""
        self.folded = True
        self.is_active = False
        self.show_cards = False

    def call(self, current_bet):
        """Поднять до текущей ставки"""
        needed = current_bet - self.total_bet
        if needed > 0:
            return self.make_bet(needed)
        elif needed == 0:
            return True
        return False

    def raise_bet(self, amount, current_bet):
        """Повысить ставку"""
        needed = current_bet + amount - self.total_bet
        if needed > 0:
            return self.make_bet(needed)
        return False

    def get_hand_string(self):
        """Получить строковое представление руки"""
        if not self.show_cards or len(self.hand) < 2:
            return "[XX] [XX]"
        return f"[{self.hand[0]}] [{self.hand[1]}]"

    def __str__(self):
        status = ""
        if self.folded:
            status = " (FOLDED)"
        elif self.all_in:
            status = " (ALL-IN)"
        return f"{self.name}: ${self.chips} Bet: ${self.bet}{status}"