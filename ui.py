import pygame
import sys
from styles import *

try:
    from game_logic import PokerGame
except ImportError as e:
    print(f"Ошибка импорта PokerGame: {e}")
    sys.exit(1)


class PokerUI:
    def __init__(self, num_players):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Texas Hold'em Poker")

        self.game = PokerGame(num_players)
        self.fonts = init_fonts()
        self.clock = pygame.time.Clock()
        self.running = True
        self.input_active = False
        self.input_text = ""
        self.num_players = num_players
        self.player_positions = get_player_positions(num_players)

        self.game.start_new_hand()
        self.current_player = self.game.players[self.game.current_player_index]
        self.current_player.show_cards = True
        self.current_player.is_turn = True

    def draw_table(self):
        self.screen.fill(BACKGROUND)

        table_rect = pygame.Rect(
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 4,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        pygame.draw.ellipse(self.screen, TABLE_COLOR, table_rect)
        pygame.draw.ellipse(self.screen, TABLE_BORDER, table_rect, 5)

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.circle(self.screen, (50, 50, 50), (center_x, center_y), 60)

        pot_text = self.fonts["title"].render(f"${self.game.pot}", True, (255, 215, 0))
        pot_rect = pot_text.get_rect(center=(center_x, center_y))
        self.screen.blit(pot_text, pot_rect)

        self.draw_game_info()

    def draw_game_info(self):

        info_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_bg)

        phase_text = self.fonts["title"].render(
            f"ТЕХАС ХОЛДЕМ | {self.game.game_phase.upper()}",
            True, TEXT_COLOR
        )
        phase_rect = phase_text.get_rect(center=(CENTER_X, 20))
        self.screen.blit(phase_text, phase_rect)

        # Текущая ставка
        bet_text = self.fonts["info"].render(
            f"Текущая ставка: ${self.game.current_bet}",
            True, (255, 215, 0)
        )
        bet_rect = bet_text.get_rect(center=(CENTER_X, 42))
        self.screen.blit(bet_text, bet_rect)

    def draw_players(self):
        for i, player in enumerate(self.game.players):
            if i >= len(self.player_positions):
                continue

            player_x, player_y = self.player_positions[i]

            # Проверяем, не пересекается ли позиция с областью информации
            #if player_x > INFO_AREA_X - 100:
                #player_x = INFO_AREA_X - 100

            # Определяем цвет игрока
            if i >= self.num_players:
                color = PLAYER_INACTIVE
            elif player == self.current_player:
                color = PLAYER_TURN
            elif player.folded:
                color = PLAYER_INACTIVE
            elif player in self.game.active_players:
                color = PLAYER_ACTIVE
            else:
                color = (180, 180, 180)

            # Рисуем кружок игрока
            pygame.draw.circle(self.screen, color, (player_x, player_y), PLAYER_RADIUS)
            pygame.draw.circle(self.screen, (0, 0, 0), (player_x, player_y), PLAYER_RADIUS, 2)

            # Имя игрока (над кружком)
            name_text = self.fonts["player"].render(player.name, True, TEXT_COLOR)
            name_rect = name_text.get_rect(center=(player_x, player_y - PLAYER_RADIUS - 12))
            self.screen.blit(name_text, name_rect)

            chips_bg_radius = PLAYER_RADIUS - 6
            pygame.draw.circle(self.screen, CHIPS_COLOR, (player_x, player_y), chips_bg_radius)
            pygame.draw.circle(self.screen, (0, 0, 0), (player_x, player_y), chips_bg_radius, 1)

            chips_text = self.fonts["chips"].render(f"${player.chips}", True, CHIPS_TEXT_COLOR)
            chips_rect = chips_text.get_rect(center=(player_x, player_y))
            self.screen.blit(chips_text, chips_rect)

            if player.bet > 0:
                bet_bg = pygame.Rect(
                    player_x - 35,
                    player_y + PLAYER_RADIUS + 3,
                    70, 18
                )
                pygame.draw.rect(self.screen, (255, 100, 100), bet_bg, border_radius=3)
                pygame.draw.rect(self.screen, (0, 0, 0), bet_bg, 1, border_radius=3)

                bet_text = self.fonts["info"].render(f"${player.bet}", True, TEXT_COLOR)
                bet_rect = bet_text.get_rect(center=(player_x, player_y + PLAYER_RADIUS + 12))
                self.screen.blit(bet_text, bet_rect)

            status = ""
            if player.folded:
                status = "FOLD"
            elif player.all_in:
                status = "ALL-IN"

            if status:
                status_bg = pygame.Rect(
                    player_x - 30,
                    player_y + PLAYER_RADIUS + 23,
                    60, 16
                )
                pygame.draw.rect(self.screen, (255, 50, 50), status_bg, border_radius=3)
                pygame.draw.rect(self.screen, (0, 0, 0), status_bg, 1, border_radius=3)

                status_text = self.fonts["info"].render(status, True, TEXT_COLOR)
                status_rect = status_text.get_rect(center=(player_x, player_y + PLAYER_RADIUS + 31))
                self.screen.blit(status_text, status_rect)


            self.draw_player_cards(player, player_x, player_y)

    def draw_player_cards(self, player, player_x, player_y):

        total_width = 2 * CARD_WIDTH + CARD_SPACING
        start_x = player_x - total_width // 2
        if start_x < 10:
            start_x = 10
        elif start_x + total_width > SCREEN_WIDTH - 10:
            start_x = SCREEN_WIDTH - total_width - 10


        if player_y < SCREEN_HEIGHT // 2:
            card_y = player_y + PLAYER_RADIUS + 40
        else:
            card_y = player_y - PLAYER_RADIUS - CARD_HEIGHT - 40

        if card_y + CARD_HEIGHT > SCREEN_HEIGHT - 120:
            card_y = SCREEN_HEIGHT - 120 - CARD_HEIGHT - 10

        if card_y < 60:
            card_y = 60

        for i in range(2):
            card_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
            show_card = False
            if i < len(player.hand):
                show_card = player.show_cards

            self.draw_card(
                player.hand[i] if i < len(player.hand) else None,
                card_x, card_y, show_card
            )

    def draw_card(self, card, x, y, visible=True):
        if visible and card:
            card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, CARD_FRONT, card_rect, border_radius=CARD_RADIUS)
            pygame.draw.rect(self.screen, (0, 0, 0), card_rect, 2, border_radius=CARD_RADIUS)

            rank_color = card.get_color()

            rank_text = self.fonts["card"].render(card.rank.value, True, rank_color)
            self.screen.blit(rank_text, (x + 6, y + 4))

            suit_text = self.fonts["card"].render(card.suit.value, True, rank_color)
            self.screen.blit(suit_text, (x + 6, y + 25))
        else:
            card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, CARD_BACK, card_rect, border_radius=CARD_RADIUS)
            pygame.draw.rect(self.screen, (0, 0, 0), card_rect, 2, border_radius=CARD_RADIUS)

    def draw_community_cards(self):
        if not self.game.community_cards:
            return

        card_positions = get_community_card_positions(len(self.game.community_cards))

        if len(self.game.community_cards) > 0:
            total_width = len(self.game.community_cards) * CARD_WIDTH + (
                        len(self.game.community_cards) - 1) * CARD_SPACING
            bg_rect = pygame.Rect(
                CENTER_X - total_width // 2 - 8,
                CENTER_Y - CARD_HEIGHT // 2 - 20,
                total_width + 16,
                CARD_HEIGHT + 40
            )
            pygame.draw.rect(self.screen, (0, 0, 0, 120), bg_rect, border_radius=6)

        for i, card in enumerate(self.game.community_cards):
            card_x, card_y = card_positions[i]
            self.draw_card(card, card_x, card_y, True)

    def draw_current_player_info(self):
        if not self.current_player:
            return

        info_bg = pygame.Rect(INFO_AREA_X, 50, INFO_AREA_WIDTH, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, INFO_BG_COLOR, info_bg, border_radius=0)

        title_text = self.fonts["player"].render("ТЕКУЩИЙ ИГРОК", True, (255, 215, 0))
        self.screen.blit(title_text, (INFO_AREA_X + 20, 70))

        name_text = self.fonts["info"].render(f"Имя: {self.current_player.name}", True, TEXT_COLOR)
        self.screen.blit(name_text, (INFO_AREA_X + 20, 100))

        cards_text = self.fonts["info"].render("Карты:", True, TEXT_COLOR)
        self.screen.blit(cards_text, (INFO_AREA_X + 20, 125))

        card_y = 150
        for i, card in enumerate(self.current_player.hand):
            if i >= 2:
                break
            if card:
                card_text = self.fonts["card"].render(str(card), True, card.get_color())
                self.screen.blit(card_text, (INFO_AREA_X + 40, card_y + i * 30))

        chips_text = self.fonts["info"].render(f"Фишки: ${self.current_player.chips}", True, TEXT_COLOR)
        self.screen.blit(chips_text, (INFO_AREA_X + 20, 210))

        bet_text = self.fonts["info"].render(f"Ставка: ${self.current_player.total_bet}", True, TEXT_COLOR)
        self.screen.blit(bet_text, (INFO_AREA_X + 20, 235))

        status = "Активен"
        if self.current_player.folded:
            status = "Сбросил"
        elif self.current_player.all_in:
            status = "Ва-банк"

        status_text = self.fonts["info"].render(f"Статус: {status}", True, TEXT_COLOR)
        self.screen.blit(status_text, (INFO_AREA_X + 20, 260))

    def draw_buttons(self):
        if not self.current_player:
            return

        buttons = [
            ("FOLD", BUTTONS["fold"], not self.current_player.folded),
            ("CHECK", BUTTONS["check"], self.current_player.total_bet >= self.game.current_bet),
            ("CALL", BUTTONS["call"], self.current_player.total_bet < self.game.current_bet and
             self.current_player.chips > 0),
            ("RAISE", BUTTONS["raise"], self.current_player.chips > 0),
            ("ALL-IN", BUTTONS["all_in"], self.current_player.chips > 0),
        ]

        mouse_pos = pygame.mouse.get_pos()

        for text, pos, enabled in buttons:
            button_width = 70
            button_height = 32
            button_rect = pygame.Rect(pos[0] - button_width // 2, pos[1] - button_height // 2, button_width,
                                      button_height)
            hover = button_rect.collidepoint(mouse_pos) and enabled

            if not enabled:
                color = (100, 100, 100)
            elif hover:
                color = BUTTON_HOVER
            else:
                color = BUTTON_COLOR

            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2, border_radius=5)

            btn_text = self.fonts["button"].render(text, True, TEXT_COLOR)
            btn_rect = btn_text.get_rect(center=button_rect.center)
            self.screen.blit(btn_text, btn_rect)

    def draw_input_box(self):
        if self.input_active:
            input_bg = pygame.Rect(CENTER_X - 120, SCREEN_HEIGHT - 180, 240, 40)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), input_bg, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), input_bg, 2, border_radius=6)
            input_rect = pygame.Rect(CENTER_X - 100, SCREEN_HEIGHT - 170, 200, 20)
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), input_rect, 1)
            input_surface = self.fonts["button"].render(self.input_text, True, (0, 0, 0))
            self.screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 2))
            hint_text = self.fonts["info"].render("Введите сумму и нажмите Enter",
                                                  True, TEXT_COLOR)
            hint_rect = hint_text.get_rect(center=(CENTER_X, SCREEN_HEIGHT - 140))
            self.screen.blit(hint_text, hint_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.input_active:
                    self.handle_button_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            amount = int(self.input_text)
                            if amount > 0 and self.current_player:
                                if self.game.player_action(self.current_player, "raise", amount):
                                    self.switch_to_next_player()
                        except ValueError:
                            pass
                        self.input_active = False
                        self.input_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isdigit():
                        self.input_text += event.unicode

    def handle_button_click(self, pos):
        button_areas = {
            "fold": pygame.Rect(BUTTONS["fold"][0] - 35, BUTTONS["fold"][1] - 16, 70, 32),
            "check": pygame.Rect(BUTTONS["check"][0] - 35, BUTTONS["check"][1] - 16, 70, 32),
            "call": pygame.Rect(BUTTONS["call"][0] - 35, BUTTONS["call"][1] - 16, 70, 32),
            "raise": pygame.Rect(BUTTONS["raise"][0] - 35, BUTTONS["raise"][1] - 16, 70, 32),
            "all_in": pygame.Rect(BUTTONS["all_in"][0] - 35, BUTTONS["all_in"][1] - 16, 70, 32),
        }

        for action, rect in button_areas.items():
            if rect.collidepoint(pos):
                self.handle_player_action(action)
                return True
        return False

    def handle_player_action(self, action):
        if not self.current_player:
            return

        print(f"Действие: {action} от {self.current_player.name}")

        success = False

        if action == "fold":
            success = self.game.player_action(self.current_player, "fold")
            if success:
                print(f"{self.current_player.name} сбросил карты")
                self.switch_to_next_player()

        elif action == "check":
            success = self.game.player_action(self.current_player, "check")
            if success:
                print(f"{self.current_player.name} сделал чек")
                self.switch_to_next_player()
            else:
                print(f"{self.current_player.name} не может сделать чек (нужен колл)")

        elif action == "call":
            success = self.game.player_action(self.current_player, "call")
            if success:
                print(f"{self.current_player.name} сделал колл")
                self.switch_to_next_player()

        elif action == "raise":
            self.input_active = True
            self.input_text = ""
            print(f"{self.current_player.name} хочет повысить ставку")
            # Ход не передается - ждем ввода суммы

        elif action == "all_in":
            success = self.game.player_action(self.current_player, "all_in")
            if success:
                print(f"{self.current_player.name} пошел ва-банк")
                self.switch_to_next_player()

    def switch_to_next_player(self):
        """Переключиться на следующего игрока"""
        if not self.current_player:
            return

        # Скрываем карты текущего игрока
        self.current_player.show_cards = False
        self.current_player.is_turn = False

        # Сохраняем предыдущего игрока
        prev_player = self.current_player

        # Ищем следующего активного игрока
        self.current_player = self.game.next_player()

        # Если нашли следующего игрока
        if self.current_player:
            # Показываем карты нового текущего игрока
            self.current_player.show_cards = True
            self.current_player.is_turn = True

            # Критически важно: проверяем завершение раунда ДО сравнения игроков
            if self.game.check_round_complete():
                # Раунд торгов завершен - переходим к следующей фазе
                print(f"Раунд торгов завершен. Переход к следующей фазе из {self.game.game_phase}")

                can_continue = self.game.next_phase()

                if not can_continue or self.game.game_phase == "showdown":
                    # Это showdown или следующая фаза недоступна
                    print("SHOWDOWN! Определение победителя...")

                    # Показываем карты всех игроков
                    for player in self.game.active_players:
                        if not player.folded:
                            player.show_cards = True

                    # Определяем победителя
                    winners = self.game.determine_winner()

                    # Показываем экран победителя
                    self.show_winner_screen(winners)
                    pygame.time.delay(2000)

                    # Возвращаемся в меню
                    self.return_to_menu = True
                    self.running = False
                    return
                else:
                    # Успешно перешли к следующей фазе
                    print(f"Новая фаза: {self.game.game_phase}")

                    # Скрываем карты всех игроков
                    for player in self.game.players:
                        player.show_cards = False

                    # Находим нового текущего игрока
                    self.current_player = self.game.players[self.game.current_player_index]
                    if self.current_player:
                        self.current_player.show_cards = True
                        self.current_player.is_turn = True
        else:
            # Не нашли следующего игрока - проверяем завершение раунда
            if self.game.check_round_complete():
                can_continue = self.game.next_phase()

                if not can_continue or self.game.game_phase == "showdown":
                    print("SHOWDOWN (нет следующего игрока)! Определение победителя...")

                    # Показываем карты всех игроков
                    for player in self.game.active_players:
                        if not player.folded:
                            player.show_cards = True

                    winners = self.game.determine_winner()
                    self.show_winner_screen(winners)
                    pygame.time.delay(2000)

                    self.return_to_menu = True
                    self.running = False

    def show_winner_screen(self, winners):
        """Показать победителя и карты всех игроков на игровом столе"""
        print("=== show_winner_screen вызван ===")

        for player in self.game.players:
            player.show_cards = True
            print(f"Показали карты {player.name} в финале")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    print("Нажата кнопка - возвращаемся в меню")
                    self.return_to_menu = True
                    self.running = False
                    return

            self.screen.fill(BACKGROUND)

            table_rect = pygame.Rect(
                SCREEN_WIDTH // 4,
                SCREEN_HEIGHT // 4,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )
            pygame.draw.ellipse(self.screen, TABLE_COLOR, table_rect)
            pygame.draw.ellipse(self.screen, TABLE_BORDER, table_rect, 5)
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            pygame.draw.circle(self.screen, (50, 50, 50), (center_x, center_y), 60)
            pot_text = self.fonts["title"].render(f"${self.game.pot}", True, (255, 215, 0))
            pot_rect = pot_text.get_rect(center=(center_x, center_y))
            self.screen.blit(pot_text, pot_rect)
            self.draw_community_cards()

            self.draw_players()

            winner_panel = pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), winner_panel)
            pygame.draw.rect(self.screen, (255, 255, 255, 100), winner_panel, 2)

            if winners:
                if len(winners) == 1:
                    winner_text = self.fonts["title"].render(
                        f"🏆 ПОБЕДИТЕЛЬ: {winners[0].name} 🏆",
                        True, (255, 215, 0)
                    )
                    win_amount_text = self.fonts["info"].render(
                        f"Выигрыш: ${self.game.pot}",
                        True, (255, 255, 255)
                    )
                else:
                    winner_names = ", ".join([w.name for w in winners])
                    winner_text = self.fonts["title"].render(
                        f"🤝 НИЧЬЯ: {winner_names} 🤝",
                        True, (255, 215, 0)
                    )
                    win_amount_text = self.fonts["info"].render(
                        f"Каждый получает: ${self.game.pot // len(winners)}",
                        True, (255, 255, 255)
                    )
            else:
                winner_text = self.fonts["title"].render(
                    "ИГРА ЗАВЕРШЕНА",
                    True, (255, 215, 0)
                )
                win_amount_text = self.fonts["info"].render(
                    "Нет победителей",
                    True, (255, 255, 255)
                )

            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
            self.screen.blit(winner_text, winner_rect)

            win_amount_rect = win_amount_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85))
            self.screen.blit(win_amount_text, win_amount_rect)
            continue_text = self.fonts["info"].render(
                "Нажмите любую кнопку для возврата в меню",
                True, (200, 200, 200)
            )
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(continue_text, continue_rect)

            phase_text = self.fonts["info"].render(
                f"Фаза: SHOWDOWN - все карты открыты",
                True, (255, 255, 100)
            )
            self.screen.blit(phase_text, (20, 20))

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        print("=== Игра началась ===")
        while self.running:
            self.handle_events()

            self.draw_table()
            self.draw_community_cards()
            self.draw_players()
            self.draw_current_player_info()
            self.draw_buttons()
            self.draw_input_box()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return getattr(self, 'return_to_menu', False)
