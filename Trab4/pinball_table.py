import math

import pygame

BACKGROUND_SPARKLES = (
    (92, 198, 0.2), (225, 200, 1.4), (384, 192, 2.8),
    (78, 302, 3.9), (210, 310, 5.1), (385, 318, 0.8),
    (86, 430, 2.1), (235, 432, 3.3), (389, 432, 4.7),
    (106, 520, 5.6), (235, 548, 1.1), (376, 520, 2.6),
    (58, 82, 0.7), (327, 78, 4.1), (186, 116, 2.9), (410, 134, 5.5),
    (71, 245, 4.6), (285, 188, 0.5), (412, 278, 2.3), (145, 319, 5.3),
    (283, 303, 1.8), (421, 372, 4.4), (200, 405, 0.9), (57, 474, 3.7),
    (281, 490, 5.8), (415, 532, 1.2), (90, 610, 3.1), (225, 681, 4.9),
    (378, 702, 0.4), (62, 742, 2.0), (427, 766, 5.0), (171, 765, 3.5),
)


def draw_background_sparkles(screen, elapsed):
    for x, y, phase in BACKGROUND_SPARKLES:
        pulse = (math.sin(elapsed * 2.8 + phase) + 1) / 2
        brightness = round(38 + pulse * 190)
        radius = 1 if pulse < 0.72 else 2
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), radius)


def draw_text(screen, text, font, color, center):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def star_points(center, outer_radius, inner_radius, rotation=0):
    points = []
    for index in range(10):
        angle = rotation - math.pi / 2 + index * math.pi / 5
        radius = outer_radius if index % 2 == 0 else inner_radius
        points.append((center[0] + math.cos(angle) * radius,
                       center[1] + math.sin(angle) * radius))
    return points


def moon_points(center, radius):
    points = []
    sample_count = 64
    inner_offset = radius * 0.46
    inner_radius = radius * 0.9
    intersection_x = (radius ** 2 - inner_radius ** 2 + inner_offset ** 2) / (2 * inner_offset)
    intersection_y = math.sqrt(radius ** 2 - intersection_x ** 2)
    outer_angle = math.atan2(intersection_y, intersection_x)

    for index in range(sample_count + 1):
        angle = -outer_angle - (2 * math.pi - 2 * outer_angle) * index / sample_count
        points.append((center[0] + math.cos(angle) * radius,
                       center[1] + math.sin(angle) * radius))

    inner_angle = math.atan2(intersection_y, intersection_x - inner_offset)
    for index in range(sample_count + 1):
        angle = inner_angle + (2 * math.pi - 2 * inner_angle) * index / sample_count
        points.append((center[0] + inner_offset + math.cos(angle) * inner_radius,
                       center[1] + math.sin(angle) * inner_radius))
    return points


def draw_crescent(screen, center, radius, fill_color, outline_color):
    scale = 4
    margin = 2
    surface_size = round((radius + margin) * 2 * scale)
    center_px = round((radius + margin) * scale)
    moon_layer = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    pygame.draw.circle(moon_layer, fill_color, (center_px, center_px), round(radius * scale))
    pygame.draw.circle(
        moon_layer,
        (*fill_color, 0),
        (center_px + round(radius * 0.46 * scale), center_px),
        round(radius * 0.9 * scale),
    )

    output_size = round((radius + margin) * 2)
    smooth_layer = pygame.transform.smoothscale(moon_layer, (output_size, output_size))
    destination = smooth_layer.get_rect(center=(round(center[0]), round(center[1])))
    screen.blit(smooth_layer, destination)
    outer_arc = moon_points(center, radius)[:65]
    pygame.draw.aalines(screen, outline_color, False,
                        [(round(x), round(y)) for x, y in outer_arc])


def draw_rounded_path(screen, points, color, width):
    coordinates = [(round(point[0]), round(point[1])) for point in points]
    pygame.draw.lines(screen, color, False, coordinates, width)
    cap_radius = max(1, width // 2)
    pygame.draw.circle(screen, color, coordinates[0], cap_radius)
    pygame.draw.circle(screen, color, coordinates[-1], cap_radius)


def draw_closed_path(screen, points, color, width):
    coordinates = [(round(point[0]), round(point[1])) for point in points]
    pygame.draw.lines(screen, color, True, coordinates, width)


def draw_launcher_area(screen, game):
    pygame.draw.rect(screen, (14, 8, 23), (413, 234, 23, 412), border_radius=10)
    pygame.draw.line(screen, (39, 27, 53), (game["SHOOTER_DIVIDER_X"], 700),
                     (game["SHOOTER_DIVIDER_X"], game["SHOOTER_EXIT_Y"]), 10)
    pygame.draw.line(screen, game["PINK"], (game["SHOOTER_DIVIDER_X"], 700),
                     (game["SHOOTER_DIVIDER_X"], game["SHOOTER_EXIT_Y"]), 2)


def draw_table(screen, game):
    BLACK = game["BLACK"]
    DEEP_BLUE = game["DEEP_BLUE"]
    PANEL = game["PANEL"]
    CYAN = game["CYAN"]
    PALE_CYAN = game["PALE_CYAN"]
    PINK = game["PINK"]
    YELLOW = game["YELLOW"]
    WHITE = game["WHITE"]
    MUTED = game["MUTED"]
    FONT_SMALL = game["FONT_SMALL"]
    FONT_MEDIUM = game["FONT_MEDIUM"]
    FONT_LARGE = game["FONT_LARGE"]
    phase = game["phase"]
    lives = game["lives"]
    score = game["score"]
    best_score = game["best_score"]
    charge = game["charge"]
    targets = game["targets"]
    flipper_extension = game["flipper_extension"]
    BALL_POS = game["BALL_POS"]
    BALL_RADIUS = game["BALL_RADIUS"]
    SHOOTER_LANE_RIGHT = game["SHOOTER_LANE_RIGHT"]
    SHOOTER_EXIT_Y = game["SHOOTER_EXIT_Y"]
    TOP_ARCH_CENTER = game["TOP_ARCH_CENTER"]
    BOTTOM_ARCH_CENTER = game["BOTTOM_ARCH_CENTER"]
    SLINGSHOT_TRIANGLES = game["SLINGSHOT_TRIANGLES"]
    FLIPPER_GUIDES = game["FLIPPER_GUIDES"]
    flipper_segments = game["flipper_segments"]
    smoothstep = game["smoothstep"]
    top_rail_points = game["top_rail_points"]
    bottom_rail_points = game["bottom_rail_points"]
    PLAYFIELD_LEFT = game["PLAYFIELD_LEFT"]
    PLAYFIELD_RIGHT = game["PLAYFIELD_RIGHT"]

    screen.fill(BLACK)
    pygame.draw.rect(screen, DEEP_BLUE, (18, 18, 454, 804), border_radius=20)
    pygame.draw.rect(screen, CYAN, (18, 18, 454, 804), width=3, border_radius=20)
    pygame.draw.rect(screen, PANEL, (33, 34, 424, 780), border_radius=15)
    draw_background_sparkles(screen, pygame.time.get_ticks() / 1000)

    top_points = top_rail_points()
    bottom_points = bottom_rail_points()
    outline_points = list(top_points)
    outline_points.extend((PLAYFIELD_RIGHT, y)
                          for y in range(int(TOP_ARCH_CENTER.y) + 5,
                                         int(BOTTOM_ARCH_CENTER.y), 5))
    outline_points.extend(bottom_points)
    outline_points.extend((PLAYFIELD_LEFT, y)
                          for y in range(int(BOTTOM_ARCH_CENTER.y) - 5,
                                         int(TOP_ARCH_CENTER.y), -5))
    draw_closed_path(screen, outline_points, (39, 27, 53), 14)
    draw_closed_path(screen, outline_points, CYAN, 3)
    pygame.draw.line(screen, (39, 27, 53), (SHOOTER_LANE_RIGHT, TOP_ARCH_CENTER.y),
                     (SHOOTER_LANE_RIGHT, BOTTOM_ARCH_CENTER.y), 10)
    pygame.draw.line(screen, MUTED, (SHOOTER_LANE_RIGHT, TOP_ARCH_CENTER.y),
                     (SHOOTER_LANE_RIGHT, BOTTOM_ARCH_CENTER.y), 3)
    for guide_start, guide_end in FLIPPER_GUIDES:
        draw_rounded_path(screen, [guide_start, guide_end], (39, 27, 53), 16)
        draw_rounded_path(screen, [guide_start, guide_end], CYAN, 5)

    for vertices in SLINGSHOT_TRIANGLES:
        points = [(round(vertex.x), round(vertex.y)) for vertex in vertices]
        pygame.draw.polygon(screen, (39, 27, 53), points)
        pygame.draw.polygon(screen, (23, 15, 34), points, 8)
        pygame.draw.polygon(screen, CYAN, points, 2)

    draw_text(screen, "VIDAS", FONT_SMALL, MUTED, (509, 326))
    for index in range(lives):
        pygame.draw.circle(screen, PINK, (500 + index * 9, 350), 4)

    draw_text(screen, "PONTOS", FONT_SMALL, MUTED, (509, 392))
    draw_text(screen, f"{score:06d}", FONT_MEDIUM, YELLOW, (509, 417))
    if phase != "playing":
        draw_text(screen, "FORCA", FONT_SMALL, WHITE, (509, 450))
        pygame.draw.rect(screen, (19, 11, 29), (488, 465, 42, 244), border_radius=9)
        pygame.draw.rect(screen, (79, 60, 99), (488, 465, 42, 244), width=2, border_radius=9)
        bar_height = 210 * charge / 100
        if bar_height > 0:
            bar_color = PINK if charge < 25 else YELLOW if charge > 78 else CYAN
            pygame.draw.rect(screen, bar_color,
                             (498, 700 - bar_height, 22, bar_height), border_radius=6)
            pygame.draw.rect(screen, WHITE,
                             (498, 700 - bar_height, 22, min(6, bar_height)), border_radius=3)
        for mark in range(1, 5):
            y = 700 - mark * 47
            pygame.draw.line(screen, (93, 72, 111), (489, y), (496, y), 2)
        draw_text(screen, f"{int(charge):02d}%", FONT_SMALL, WHITE, (509, 721))

    for target in targets:
        target["flash"] = max(0.0, target["flash"] - 0.045)
        pulse = target["flash"]
        pulse_scale = 4 if target["kind"] == "moon" else 6
        radius = target["radius"] + int(pulse * pulse_scale)
        color = WHITE if pulse > 0.35 else target["color"]
        if target["kind"] == "bumper":
            pygame.draw.circle(screen, (10, 6, 17), target["pos"], radius + 6)
            pygame.draw.circle(screen, color, target["pos"], radius + 4, 2)
            pygame.draw.circle(screen, (35, 21, 49), target["pos"], radius)
            pygame.draw.circle(screen, color, target["pos"], radius, 3)
            pygame.draw.circle(screen, WHITE, target["pos"], 5 + int(pulse * 3))
        elif target["kind"] == "moon":
            draw_crescent(screen, target["pos"], radius, WHITE, PALE_CYAN)
        else:
            points = star_points(target["pos"], radius + 5, radius * 0.43,
                                 pulse * 0.18)
            pygame.draw.polygon(screen, (29, 18, 40), points)
            pygame.draw.polygon(screen, color, points, 3)
            pygame.draw.circle(screen, WHITE, target["pos"], 3 + int(pulse * 3))

    active_flippers = smoothstep(flipper_extension)
    flipper_color = tuple(round(rest + (active - rest) * active_flippers)
                          for rest, active in zip(CYAN, YELLOW))
    for start, end in flipper_segments(flipper_extension):
        draw_rounded_path(screen, [start, end], (39, 27, 53), 32)
        draw_rounded_path(screen, [start, end], (23, 15, 34), 24)
        draw_rounded_path(screen, [start, end], flipper_color, 15)
        draw_rounded_path(screen, [start, end], PALE_CYAN, 3)
        pygame.draw.circle(screen, (39, 27, 53), start, 17)
        pygame.draw.circle(screen, CYAN, start, 13, 2)
        pygame.draw.circle(screen, WHITE, start, 5)
    if phase == "ready":
        draw_text(screen, "SEGURE ESPACO", FONT_MEDIUM, WHITE, (225, 528))
        draw_text(screen, "PARA CARREGAR", FONT_SMALL, PALE_CYAN, (225, 549))
    elif phase == "charging":
        draw_text(screen, "SOLTE PARA LANCAR", FONT_SMALL, YELLOW, (225, 540))
    elif phase == "game_over":
        pygame.draw.rect(screen, (10, 6, 17), (55, 274, 355, 158), border_radius=10)
        pygame.draw.rect(screen, CYAN, (55, 274, 355, 158), width=2, border_radius=10)
        draw_text(screen, "FIM DE JOGO", FONT_LARGE, WHITE, (232, 301))
        draw_text(screen, f"PONTOS: {score:06d}", FONT_MEDIUM, PALE_CYAN, (232, 339))
        draw_text(screen, f"RECORDE: {best_score:06d}", FONT_MEDIUM, YELLOW, (232, 370))
        draw_text(screen, "ESPACO PARA RECOMECAR", FONT_SMALL, MUTED, (232, 407))

    if phase in ("ready", "charging"):
        draw_launcher_area(screen, game)

    pygame.draw.circle(screen, WHITE, BALL_POS, BALL_RADIUS + 2)
    pygame.draw.circle(screen, (123, 105, 145), BALL_POS, BALL_RADIUS)
    pygame.draw.circle(screen, WHITE, (int(BALL_POS.x - 3), int(BALL_POS.y - 3)), 3)
