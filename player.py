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