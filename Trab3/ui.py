import pygame
from util import draw_text, draw_bar
from enemy import Boss


def draw_hud(screen, player, wave_manager, objects=None):
    objects = objects if objects is not None else []
    draw_bar(screen, (10, 10), (200, 16), player.stats.hp / player.stats.max_hp, (60, 0, 0), (200, 30, 30))
    draw_text(screen, f"HP {int(player.stats.hp)}/{int(player.stats.max_hp)}", (14, 11), size=14)

    draw_bar(screen, (10, 30), (200, 12), player.stats.mana / player.stats.max_mana, (0, 0, 60), (60, 90, 220))
    draw_text(screen, f"MP {int(player.stats.mana)}/{int(player.stats.max_mana)}", (14, 31), size=12)

    draw_bar(screen, (10, 46), (200, 10), player.stats.xp / player.stats.xp_to_next, (40, 40, 10), (230, 210, 60))
    draw_text(screen, f"Nv. {player.stats.level}", (220, 44), size=14)

    draw_text(screen, f"Onda {wave_manager.wave}", (10, 64), size=18, color=(255, 255, 255))
    draw_text(screen, f"Moedas: {player.stats.coins}", (10, 84), size=16, color=(255, 215, 0))

    boss = next((obj for obj in objects if isinstance(obj, Boss) and obj.alive), None)
    if boss:
        draw_boss_bar(screen, boss)

    controls = ["Botão direito: Magia básica", "SPACE: Dash"]
    if player.has_fireball:
        controls.append("TAB: Bola de Fogo")
    if player.has_chain_lightning:
        controls.append("Q: Raio em Cadeia")
    if player.has_blizzard:
        controls.append("E: Nevasca em Cone")
    if player.has_force_field:
        controls.append("R: Campo de Força")

    w, h = screen.get_size()
    x = w - 210
    y = h - 18 * len(controls) - 6
    for line in controls:
        draw_text(screen, line, (x, y), size=13, color=(200, 200, 200))
        y += 18


def draw_boss_bar(screen, boss):
    """Desenha o nome e a barra de vida do Boss no topo da tela."""
    w, _h = screen.get_size()
    bar_width = min(900, w - 360)
    bar_height = 28
    x = (w - bar_width) // 2
    bar_y = 64

    draw_text(
        screen,
        "O Grande Dragão Gordo",
        (w // 2, 34),
        size=30,
        color=(255, 220, 145),
        center=True,
        font_name="Georgia",
    )
    pygame.draw.rect(screen, (35, 8, 8), (x - 4, bar_y - 4, bar_width + 8, bar_height + 8), border_radius=5)
    draw_bar(
        screen,
        (x, bar_y),
        (bar_width, bar_height),
        boss.hp / boss.max_hp,
        (75, 10, 10),
        (220, 35, 35),
        border_color=(255, 190, 80),
    )


def draw_level_up(screen, upgrades):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    draw_text(screen, "LEVEL UP! Escolha uma melhoria (1, 2 ou 3)", (w // 2, 90), size=28, color=(255, 255, 255), center=True)

    card_w, card_h = 180, 240
    gap = 30
    total_w = len(upgrades) * card_w + (len(upgrades) - 1) * gap
    start_x = w // 2 - total_w // 2
    y = h // 2 - card_h // 2

    for i, up in enumerate(upgrades):
        x = start_x + i * (card_w + gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(screen, (25, 25, 25), rect, border_radius=10)
        pygame.draw.rect(screen, up.rarity["color"], rect, width=4, border_radius=10)

        draw_text(screen, up.rarity["name"], (rect.centerx, rect.top + 24), size=16, color=up.rarity["color"], center=True)
        draw_text(screen, up.label, (rect.centerx, rect.top + 70), size=18, color=(255, 255, 255), center=True)
        draw_text(screen, up.description, (rect.centerx, rect.top + 120), size=13, color=(220, 220, 220), center=True)
        draw_text(screen, f"[{i + 1}]", (rect.centerx, rect.bottom - 24), size=18, color=(180, 180, 180), center=True)


def draw_shop_icon(screen, item_name, center, purchased=False):
    """Desenha um pequeno simbolo visual para identificar cada oferta."""
    cx, cy = center
    faded = purchased
    outline = (105, 125, 130) if faded else (230, 235, 220)
    name = item_name.lower()

    if "poção" in name:
        pygame.draw.rect(screen, outline, (cx - 5, cy - 20, 10, 7), border_radius=2)
        pygame.draw.polygon(screen, (205, 45, 55), [(cx - 14, cy - 12), (cx + 14, cy - 12),
                          (cx + 10, cy + 17), (cx - 10, cy + 17)])
        pygame.draw.line(screen, outline, (cx - 10, cy - 5), (cx + 10, cy - 5), 2)
    elif "elmo" in name:
        pygame.draw.arc(screen, outline, (cx - 19, cy - 19, 38, 38), 0, 3.14, 4)
        pygame.draw.line(screen, outline, (cx - 18, cy), (cx + 18, cy), 4)
        pygame.draw.line(screen, outline, (cx, cy - 17), (cx, cy + 8), 3)
    elif "botas" in name:
        pygame.draw.polygon(screen, (100, 180, 220), [(cx - 16, cy - 17), (cx - 2, cy - 17),
                          (cx + 2, cy + 7), (cx + 18, cy + 7), (cx + 18, cy + 16),
                          (cx - 10, cy + 16), (cx - 16, cy + 7)])
    elif "lâmina" in name:
        pygame.draw.polygon(screen, outline, [(cx - 16, cy + 14), (cx + 15, cy - 17),
                          (cx + 20, cy - 12), (cx - 11, cy + 19)])
        pygame.draw.line(screen, (220, 170, 65), (cx - 17, cy + 14), (cx - 5, cy + 2), 4)
    elif "amuleto arcano" in name:
        pygame.draw.arc(screen, (210, 175, 70), (cx - 18, cy - 19, 36, 34), 0.25, 2.9, 3)
        pygame.draw.line(screen, (210, 175, 70), (cx - 9, cy + 10), (cx, cy + 16), 3)
        pygame.draw.line(screen, (210, 175, 70), (cx + 9, cy + 10), (cx, cy + 16), 3)
        pygame.draw.circle(screen, (105, 35, 180), (cx, cy + 17), 8)
        pygame.draw.circle(screen, (190, 100, 255), (cx - 2, cy + 14), 3)
        pygame.draw.circle(screen, (225, 170, 255), (cx - 3, cy + 13), 1)
    elif "núcleo arcano" in name:
        pygame.draw.circle(screen, (95, 35, 150), (cx, cy), 21)
        pygame.draw.circle(screen, (150, 65, 225), (cx, cy), 16)
        pygame.draw.polygon(screen, (130, 45, 210), [(cx, cy - 19), (cx + 15, cy),
                          (cx, cy + 19), (cx - 15, cy)])
        pygame.draw.polygon(screen, (205, 120, 255), [(cx, cy - 13), (cx + 7, cy),
                          (cx, cy + 12), (cx - 7, cy)])
        pygame.draw.line(screen, (245, 205, 255), (cx - 3, cy - 9), (cx + 4, cy - 2), 2)
    elif "cajado rúnico" in name:
        pygame.draw.line(screen, (105, 60, 30), (cx - 14, cy + 19), (cx + 8, cy - 14), 7)
        pygame.draw.line(screen, (170, 105, 50), (cx - 12, cy + 16), (cx + 8, cy - 14), 2)
        pygame.draw.circle(screen, (40, 160, 75), (cx + 10, cy - 18), 12)
        pygame.draw.polygon(screen, (80, 220, 115), [(cx + 10, cy - 30), (cx + 19, cy - 18),
                          (cx + 10, cy - 6), (cx + 1, cy - 18)])
        pygame.draw.line(screen, (190, 255, 205), (cx + 6, cy - 23), (cx + 12, cy - 16), 2)
    elif "grimório de fogo" in name:
        pygame.draw.polygon(screen, (80, 35, 25), [(cx - 21, cy - 12), (cx - 2, cy - 7),
                          (cx - 2, cy + 20), (cx - 22, cy + 14)])
        pygame.draw.polygon(screen, (100, 45, 30), [(cx + 2, cy - 7), (cx + 21, cy - 12),
                          (cx + 22, cy + 14), (cx + 2, cy + 20)])
        pygame.draw.line(screen, (230, 190, 125), (cx, cy - 7), (cx, cy + 19), 2)
        pygame.draw.line(screen, (210, 155, 100), (cx - 16, cy - 5), (cx - 6, cy - 2), 2)
        pygame.draw.line(screen, (210, 155, 100), (cx + 6, cy - 2), (cx + 16, cy - 5), 2)
        pygame.draw.polygon(screen, (220, 45, 25), [(cx, cy - 8), (cx - 9, cy - 20),
                          (cx - 7, cy - 31), (cx + 1, cy - 22), (cx + 9, cy - 34),
                          (cx + 8, cy - 18), (cx + 15, cy - 23), (cx + 9, cy - 7)])
        pygame.draw.polygon(screen, (255, 170, 35), [(cx, cy - 10), (cx - 4, cy - 21),
                          (cx + 1, cy - 17), (cx + 7, cy - 25), (cx + 5, cy - 10)])
    elif "raio" in name or "fogo" in name or "cajado" in name or "arcano" in name:
        pygame.draw.polygon(screen, (240, 185, 55), [(cx + 4, cy - 21), (cx - 13, cy + 1),
                          (cx - 2, cy + 1), (cx - 8, cy + 20), (cx + 15, cy - 7),
                          (cx + 3, cy - 7)])
    elif "gelo" in name:
        pygame.draw.line(screen, (125, 215, 245), (cx, cy - 20), (cx, cy + 20), 3)
        pygame.draw.line(screen, (125, 215, 245), (cx - 17, cy - 10), (cx + 17, cy + 10), 3)
        pygame.draw.line(screen, (125, 215, 245), (cx + 17, cy - 10), (cx - 17, cy + 10), 3)
    elif "coração" in name:
        pygame.draw.polygon(screen, (225, 75, 90), [(cx, cy + 18), (cx - 19, cy - 3),
                          (cx - 17, cy - 14), (cx - 7, cy - 19), (cx, cy - 11),
                          (cx + 7, cy - 19), (cx + 17, cy - 14), (cx + 19, cy - 3)])
    elif "conhecimento" in name:
        pygame.draw.circle(screen, (25, 80, 170), (cx, cy), 21)
        pygame.draw.circle(screen, (45, 145, 245), (cx, cy), 16)
        pygame.draw.circle(screen, (115, 215, 255), (cx - 5, cy - 6), 6)
        pygame.draw.circle(screen, (220, 250, 255), (cx - 7, cy - 8), 2)
        pygame.draw.circle(screen, (105, 205, 255), (cx - 24, cy - 8), 3)
        pygame.draw.circle(screen, (135, 220, 255), (cx + 22, cy + 7), 3)
        pygame.draw.circle(screen, (185, 240, 255), (cx + 9, cy - 23), 2)
    else:
        pygame.draw.circle(screen, (215, 175, 55), (cx, cy), 18)
        pygame.draw.circle(screen, outline, (cx, cy), 13, 2)
        draw_text(screen, "+", (cx, cy - 2), size=20, color=outline, center=True)


def draw_shop(screen, items, coins):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((8, 12, 18, 235))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(90, 42, w - 180, h - 84)
    pygame.draw.rect(screen, (18, 26, 36), panel, border_radius=4)
    pygame.draw.rect(screen, (110, 150, 175), panel, width=2, border_radius=4)
    pygame.draw.line(screen, (110, 150, 175), (panel.left + 28, 112), (panel.right - 28, 112), 2)

    draw_text(screen, "MERCADO", (panel.left + 30, panel.top + 22), size=28, color=(235, 245, 250))
    draw_text(screen, "Escolha uma oferta  •  ENTER continua", (panel.right - 30, panel.top + 30), size=15,
              color=(175, 195, 205), center=True)
    draw_text(screen, f"Moedas: {coins}", (panel.left + 30, panel.top + 70), size=17,
              color=(255, 215, 70))

    row_x = panel.left + 28
    row_w = panel.width - 56
    row_h = 76
    gap = 10
    start_y = 132

    for i, item in enumerate(items):
        y = start_y + i * (row_h + gap)
        rect = pygame.Rect(row_x, y, row_w, row_h)
        purchased = item.purchased
        bg = (42, 54, 58) if purchased else (25, 38, 52)
        border = (90, 130, 120) if purchased else (65, 105, 135)
        pygame.draw.rect(screen, bg, rect, border_radius=3)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=3)

        key_rect = pygame.Rect(rect.left + 14, rect.top + 14, 48, 48)
        key_color = (205, 165, 55) if not purchased else (85, 115, 105)
        pygame.draw.rect(screen, key_color, key_rect, border_radius=3)
        pygame.draw.rect(screen, (255, 235, 150) if not purchased else (135, 160, 150), key_rect, width=2, border_radius=3)
        draw_text(screen, str(i + 1), (key_rect.centerx, key_rect.centery - 5), size=22, color=(20, 25, 28), center=True)
        draw_text(screen, "COMPRAR", (key_rect.centerx, key_rect.bottom + 9), size=10, color=key_color, center=True)

        icon_rect = pygame.Rect(rect.left + 84, rect.top + 8, 60, 60)
        pygame.draw.rect(screen, (13, 22, 30), icon_rect, border_radius=3)
        draw_shop_icon(screen, item.name, icon_rect.center, purchased)

        draw_text(screen, item.name, (rect.left + 158, rect.top + 12), size=18, color=(245, 245, 235))
        draw_text(screen, item.description, (rect.left + 158, rect.top + 41), size=14, color=(180, 195, 202))

        if purchased:
            pygame.draw.rect(screen, (45, 90, 70), (rect.right - 160, rect.top + 16, 130, 44), border_radius=4)
            draw_text(screen, "COMPRADO", (rect.right - 95, rect.centery), size=16, color=(145, 245, 180), center=True)
        else:
            price_rect = pygame.Rect(rect.right - 190, rect.top + 10, 160, 56)
            pygame.draw.rect(screen, (92, 67, 18), price_rect, border_radius=4)
            pygame.draw.rect(screen, (238, 190, 55), price_rect, width=2, border_radius=4)
            coin_center = (price_rect.left + 22, price_rect.centery)
            pygame.draw.circle(screen, (255, 215, 70), coin_center, 12)
            pygame.draw.circle(screen, (135, 95, 20), coin_center, 8, 2)
            draw_text(screen, str(item.cost), (price_rect.left + 58, price_rect.centery), size=20,
                      color=(255, 235, 150), center=True)
            draw_text(screen, "OURO", (price_rect.left + 119, price_rect.centery), size=11,
                      color=(255, 215, 90), center=True)


def draw_game_over(screen, wave_reached):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "VOCÊ MORREU", (w // 2, h // 2 - 20), size=48, color=(255, 60, 60), center=True)
    draw_text(screen, f"Onda alcançada: {wave_reached}", (w // 2, h // 2 + 30), size=24, color=(255, 255, 255), center=True)
