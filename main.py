import pygame
import sys
from ui import PokerUI


def get_player_count():
    """Получить количество игроков от пользователя"""
    pygame.init()
    screen = pygame.display.set_mode((600, 500))  # Меньшее меню
    pygame.display.set_caption("Texas Hold'em - Выбор игроков")

    font_large = pygame.font.SysFont("arial", 36, bold=True)
    font_medium = pygame.font.SysFont("arial", 28)
    font_small = pygame.font.SysFont("arial", 20)

    player_count = 3
    buttons = []

    for i in range(2, 7):
        buttons.append({
            "num": i,
            "rect": pygame.Rect(150 + (i - 2) * 60, 200, 50, 50),
            "text": str(i)
        })

    running = True
    while running:
        screen.fill((34, 139, 34))

        title = font_large.render("TEXAS HOLD'EM", True, (255, 215, 0))
        screen.blit(title, (600 // 2 - title.get_width() // 2, 60))

        subtitle = font_medium.render("ПОКЕР", True, (255, 255, 255))
        screen.blit(subtitle, (600 // 2 - subtitle.get_width() // 2, 110))

        instr = font_medium.render("Количество игроков:", True, (255, 255, 255))
        screen.blit(instr, (600 // 2 - instr.get_width() // 2, 160))

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            color = (220, 20, 60) if button["num"] == player_count else (100, 100, 100)
            if button["rect"].collidepoint(mouse_pos):
                color = (255, 69, 0) if button["num"] == player_count else (150, 150, 150)

            pygame.draw.rect(screen, color, button["rect"], border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2, border_radius=8)

            num_text = font_medium.render(button["text"], True, (255, 255, 255))
            screen.blit(num_text, (
                button["rect"].x + button["rect"].width // 2 - num_text.get_width() // 2,
                button["rect"].y + button["rect"].height // 2 - num_text.get_height() // 2
            ))

        start_rect = pygame.Rect(600 // 2 - 80, 320, 160, 50)
        start_color = (50, 205, 50) if start_rect.collidepoint(mouse_pos) else (0, 180, 0)

        pygame.draw.rect(screen, start_color, start_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), start_rect, 2, border_radius=8)

        start_text = font_medium.render("ИГРАТЬ", True, (255, 255, 255))
        screen.blit(start_text, (
            start_rect.x + start_rect.width // 2 - start_text.get_width() // 2,
            start_rect.y + start_rect.height // 2 - start_text.get_height() // 2
        ))


        instruction = font_small.render("Играйте, передавая устройство по очереди", True, (200, 200, 200))
        screen.blit(instruction, (600 // 2 - instruction.get_width() // 2, 400))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            player_count = button["num"]


                    if start_rect.collidepoint(event.pos):
                        running = False

        pygame.display.flip()

    return player_count


def main():
    """Основная функция"""
    print("=" * 45)
    print("Texas Hold'em Poker")
    print("Игра для нескольких игроков за одним устройством")
    print("=" * 45)

    while True:
        num_players = get_player_count()
        print(f"Начинаем игру с {num_players} игроками...")
        game_ui = PokerUI(num_players)
        should_return_to_menu = game_ui.run()
        if not should_return_to_menu:
            break

    print("Игра завершена.")


if __name__ == "__main__":
    main()