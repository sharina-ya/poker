from enum import Enum
from collections import Counter
from deck import Dealer, Card, Suit, Rank
from player import Player


class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class PokerHand:
    def __init__(self, cards):
        self.cards = sorted(cards, key=lambda x: x.rank.value_int, reverse=True)
        self.rank = self.evaluate_hand()

    def evaluate_hand(self):
        """Оценить силу руки"""
        if len(self.cards) < 5:
            return (HandRank.HIGH_CARD, [card.rank.value_int for card in self.cards[:5]])

        values = [card.rank.value_int for card in self.cards]
        suits = [card.suit for card in self.cards]

        suit_counts = Counter(suits)
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break

        value_counts = Counter(values)
        sorted_values = sorted(values, reverse=True)

        straight_cards = self._find_straight(values)

        pairs = []
        three_of_a_kind = None
        four_of_a_kind = None

        for value, count in value_counts.items():
            if count == 2:
                pairs.append(value)
            elif count == 3:
                three_of_a_kind = value
            elif count == 4:
                four_of_a_kind = value

        pairs.sort(reverse=True)

        # Проверка комбинаций
        if flush_suit and straight_cards:
            flush_cards = [card for card in self.cards if card.suit == flush_suit]
            flush_values = [card.rank.value_int for card in flush_cards]
            straight_flush = self._find_straight(flush_values)
            if straight_flush:
                if max(straight_flush) == 14:
                    return (HandRank.ROYAL_FLUSH, straight_flush)
                return (HandRank.STRAIGHT_FLUSH, straight_flush)

        if four_of_a_kind:
            kicker = max([v for v in values if v != four_of_a_kind])
            return (HandRank.FOUR_OF_A_KIND, [four_of_a_kind] * 4 + [kicker])

        if three_of_a_kind and pairs:
            return (HandRank.FULL_HOUSE, [three_of_a_kind] * 3 + [max(pairs)] * 2)

        if flush_suit:
            flush_values = [card.rank.value_int for card in self.cards if card.suit == flush_suit]
            return (HandRank.FLUSH, sorted(flush_values[:5], reverse=True))

        if straight_cards:
            return (HandRank.STRAIGHT, straight_cards)

        if three_of_a_kind:
            kickers = sorted([v for v in values if v != three_of_a_kind], reverse=True)[:2]
            return (HandRank.THREE_OF_A_KIND, [three_of_a_kind] * 3 + kickers)

        if len(pairs) >= 2:
            top_pairs = sorted(pairs, reverse=True)[:2]
            kicker = max([v for v in values if v not in top_pairs])
            return (HandRank.TWO_PAIR, top_pairs * 2 + [kicker])

        if len(pairs) == 1:
            kickers = sorted([v for v in values if v != pairs[0]], reverse=True)[:3]
            return (HandRank.PAIR, [pairs[0]] * 2 + kickers)

        return (HandRank.HIGH_CARD, sorted_values[:5])

    def _find_straight(self, values):
        unique_values = sorted(set(values), reverse=True)

        if set([14, 2, 3, 4, 5]).issubset(set(values)):
            return [5, 4, 3, 2, 14]

        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i + 4] == 4:
                return unique_values[i:i + 5]
        return None

    def compare(self, other_hand):
        rank1, cards1 = self.rank
        rank2, cards2 = other_hand.rank

        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            for c1, c2 in zip(cards1, cards2):
                if c1 > c2:
                    return 1
                elif c1 < c2:
                    return -1
            return 0


class PokerGame:
    def __init__(self, num_players):
        self.players = []
        self.dealer = Dealer()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.small_blind = 10
        self.big_blind = 20
        self.game_phase = "preflop"
        self.active_players = []
        self.current_player_index = 0
        self.num_players = num_players
        self.round_start_index = 0
        self.players_acted_in_round = set()

        for i in range(num_players):
            name = f"Игрок {i + 1}"
            player = Player(name, i)
            self.players.append(player)
            self.active_players.append(player)

    def start_new_hand(self):
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"
        self.players_acted_in_round = set()

        print("Дилер получает публичные ключи игроков...")
        for player in self.players:
            self.dealer.players_public_keys.append((player.public_key, player))

        print("Полученные публичные ключи:")
        print(self.dealer.players_public_keys)

        print("Игроки получают публичный ключ дилера...")
        for player in self.players:
            player.dealer_public_key = self.dealer.public_key
            print(f"{player.name} получил от сервера ключ", player.dealer_public_key)

        self.dealer.initial_shuffle()

        for player in self.players:
            player.reset_hand()

        for _ in range(2):
            for player in self.players:
                if player.is_active:
                    card_enc, signature = self.dealer.get_card_for_player(player.public_key)

                    player.decrypt_card(card_enc, signature)

        self._post_blinds()

        self.active_players = [p for p in self.players if p.is_active]
        self.round_start_index = (self.dealer_position + 3) % len(self.players)
        self.current_player_index = self.round_start_index

        if self.active_players:
            current_player = self.players[self.current_player_index]
            while current_player.folded or not current_player.is_active:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                current_player = self.players[self.current_player_index]
                if self.current_player_index == self.round_start_index:
                    break

    def _post_blinds(self):
        if len(self.players) < 2:
            return

        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)

        if sb_pos < len(self.players):
            self.players[sb_pos].make_bet(self.small_blind)
            self.players_acted_in_round.add(self.players[sb_pos])

        if bb_pos < len(self.players):
            self.players[bb_pos].make_bet(self.big_blind)
            self.players_acted_in_round.add(self.players[bb_pos])
            self.current_bet = self.big_blind

        self.pot = self.small_blind + self.big_blind

    def check_round_complete(self):
        """Проверить, завершен ли текущий раунд торгов"""
        active_not_folded = [p for p in self.active_players if not p.folded]

        if len(active_not_folded) <= 1:
            return True

        all_acted = all(p in self.players_acted_in_round for p in active_not_folded)

        bets_equal = all(p.total_bet == self.current_bet for p in active_not_folded)

        if self.current_bet == 0 and all_acted:
            return True

        return all_acted and bets_equal

    def next_phase(self):
        phases = ["preflop", "flop", "turn", "river", "showdown"]

        try:
            current_index = phases.index(self.game_phase)
        except ValueError:
            current_index = 0

        if current_index < len(phases) - 1:

            self.game_phase = phases[current_index + 1]

            self.current_bet = 0
            self.players_acted_in_round = set()

            for player in self.active_players:
                player.bet = 0

            if self.game_phase == "flop":
                for _ in range(3):
                    card = self.dealer.draw()

                    if card:
                        self.community_cards.append(card)
            elif self.game_phase in ["turn", "river"]:
                card = self.dealer.draw()

                if card:
                    self.community_cards.append(card)

            if self.game_phase == "showdown":
                for player in self.active_players:

                    if not player.folded:
                        player.show_cards = True
                return True

            start_pos = (self.dealer_position + 1) % len(self.players)
            for i in range(len(self.players)):
                idx = (start_pos + i) % len(self.players)
                player = self.players[idx]
                if player in self.active_players and not player.folded:
                    self.current_player_index = idx
                    self.round_start_index = idx
                    break

            return True

        return False

    def player_action(self, player, action, amount=0):
        if player.folded or not player.is_active:
            return False

        self.players_acted_in_round.add(player)

        if action == "fold":
            player.fold()
            if player in self.active_players:
                self.active_players.remove(player)
            return True

        elif action == "check":

            if player.total_bet < self.current_bet:
                return False
            return True

        elif action == "call":
            needed = self.current_bet - player.total_bet
            if needed > 0:
                if player.make_bet(needed):
                    self.pot += needed
                    return True
                return False
            return True

        elif action == "raise":
            if amount <= 0:
                return False

            min_raise = self.current_bet
            if amount < min_raise and player.chips >= min_raise:
                return False

            total_needed = self.current_bet + amount - player.total_bet
            if total_needed > 0:
                if player.make_bet(total_needed):
                    self.current_bet = player.total_bet
                    self.pot += total_needed
                    self.players_acted_in_round = {player}
                    return True
            return False

        elif action == "all_in":
            all_in_amount = player.chips
            if player.make_bet(all_in_amount):
                if player.total_bet > self.current_bet:
                    self.current_bet = player.total_bet
                    self.players_acted_in_round = {player}
                self.pot += all_in_amount
                return True

        return False

    def next_player(self):
        if not self.active_players:
            return None

        start_index = self.current_player_index

        for i in range(1, len(self.players) + 1):
            next_index = (start_index + i) % len(self.players)
            player = self.players[next_index]

            if player in self.active_players and not player.folded:
                self.current_player_index = next_index
                return player

        return None

    def determine_winner(self):
        for player in self.active_players:
            if not player.folded:
                player.show_cards = True

        active_not_folded = [p for p in self.active_players if not p.folded]
        if len(active_not_folded) == 1:
            winner = active_not_folded[0]
            winner.chips += self.pot
            return [winner]

        if not active_not_folded:

            win_amount = self.pot // len(self.players)
            for player in self.players:
                player.chips += win_amount
            return []

        best_hand = None
        winners = []

        for player in active_not_folded:
            all_cards = player.hand + self.community_cards
            hand = PokerHand(all_cards)

            if best_hand is None:
                best_hand = hand
                winners = [player]
            else:
                comparison = hand.compare(best_hand)
                if comparison > 0:
                    best_hand = hand
                    winners = [player]
                elif comparison == 0:
                    winners.append(player)

        if winners:
            win_amount = self.pot // len(winners)
            remainder = self.pot % len(winners)

            for i, winner in enumerate(winners):
                winner.chips += win_amount
                if i == 0:
                    winner.chips += remainder

        return winners