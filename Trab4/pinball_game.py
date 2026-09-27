import pygame
import math

from pinball_save import load_best_score, save_best_score
from pinball_table import draw_table, moon_points, star_points


pygame.init()
SCREEN_WIDTH = 560
WINDOW_WIDTH = 640
SCREEN_HEIGHT = 840
FPS = 60

window = None
screen = None
clock = None

BLACK = (5, 3, 10)
DEEP_BLUE = (13, 8, 21)
PANEL = (21, 12, 32)
CYAN = (145, 92, 198)
PALE_CYAN = (205, 174, 235)
PINK = (98, 55, 132)
YELLOW = (185, 143, 224)
WHITE = (239, 229, 247)
MUTED = (135, 112, 151)


best_score = load_best_score()

FONT_SMALL = pygame.font.SysFont("consolas", 15, bold=True)
FONT_MEDIUM = pygame.font.SysFont("consolas", 21, bold=True)
FONT_LARGE = pygame.font.SysFont("consolas", 34, bold=True)

BALL_RADIUS = 9
PLAYFIELD_LEFT = 40
PLAYFIELD_RIGHT = 441
PLAYFIELD_CENTER_X = (PLAYFIELD_LEFT + PLAYFIELD_RIGHT) / 2
SHOOTER_DIVIDER_X = 410
SHOOTER_LANE_RIGHT = 441
SHOOTER_EXIT_Y = 290
TOP_ARCH_CENTER = pygame.Vector2(PLAYFIELD_CENTER_X, 230)
TOP_ARCH_RADIUS = (PLAYFIELD_RIGHT - PLAYFIELD_LEFT) / 2
TOP_ARCH_INNER_RADIUS = TOP_ARCH_RADIUS - BALL_RADIUS
TOP_ARCH_APEX_Y = TOP_ARCH_CENTER.y - TOP_ARCH_RADIUS
BOTTOM_ARCH_CENTER = pygame.Vector2(TOP_ARCH_CENTER.x, 600)
BOTTOM_ARCH_RADIUS = TOP_ARCH_RADIUS
FLIPPER_PIVOTS = (pygame.Vector2(PLAYFIELD_CENTER_X - 84.5, 646),
                  pygame.Vector2(PLAYFIELD_CENTER_X + 84.5, 646))
FLIPPER_REST_TIPS = (pygame.Vector2(PLAYFIELD_CENTER_X - 35.5, 669),
                     pygame.Vector2(PLAYFIELD_CENTER_X + 35.5, 669))
FLIPPER_ACTIVE_TIPS = (pygame.Vector2(PLAYFIELD_CENTER_X - 17.5, 601),
                       pygame.Vector2(PLAYFIELD_CENTER_X + 17.5, 601))
FLIPPER_GUIDE_END_GAP = 26.5
FLIPPER_GUIDES = (
    (FLIPPER_PIVOTS[0], pygame.Vector2(PLAYFIELD_LEFT + FLIPPER_GUIDE_END_GAP, 600)),
    (FLIPPER_PIVOTS[1], pygame.Vector2(PLAYFIELD_RIGHT - FLIPPER_GUIDE_END_GAP, 600)),
)
SLINGSHOT_TRIANGLES = (
    (pygame.Vector2(PLAYFIELD_LEFT, 475), pygame.Vector2(PLAYFIELD_LEFT, 565),
     pygame.Vector2(PLAYFIELD_LEFT + 35, 520)),
    (pygame.Vector2(PLAYFIELD_RIGHT, 475), pygame.Vector2(PLAYFIELD_RIGHT, 565),
     pygame.Vector2(PLAYFIELD_RIGHT - 35, 520)),
)
SLINGSHOT_ENTRY_Y = max(vertex.y for triangle in SLINGSHOT_TRIANGLES
                        for vertex in triangle) + BALL_RADIUS
SLINGSHOT_TOP_Y = min(vertex.y for triangle in SLINGSHOT_TRIANGLES
                       for vertex in triangle)
MAX_LAUNCH_GUIDE_CHARGE = 95
MAX_LAUNCH_GUIDE_Y = 205
MOON_GUIDE_DURATION = 10.0
FLIPPER_RAISE_SPEED = 0.22
FLIPPER_LOWER_SPEED = 0.15
GRAVITY = 0.22
BALL_START = pygame.Vector2(425.5, 630)
BALL_POS = pygame.Vector2(BALL_START)
BALL_VELOCITY = pygame.Vector2()

score = 0
lives = 3
phase = "ready"
charge = 0.0
charge_direction = 1
space_held = False
ball_in_playfield = False
slingshots_active = False
moon_guide_stage = 0
moon_guide_curve = ()
moon_guide_progress = 0.0
flipper_extension = 0.0
message_timer = 0.0


def finish_game():
    global phase, best_score
    phase = "game_over"
    if score > best_score:
        best_score = score
        save_best_score(best_score)


targets = [
    {"kind": "moon", "pos": pygame.Vector2(PLAYFIELD_CENTER_X, 105), "radius": 26, "points": 500, "color": WHITE, "flash": 0.0},
    {"kind": "bumper", "pos": pygame.Vector2(145.5, 145), "radius": 23, "points": 100, "color": CYAN, "flash": 0.0},
    {"kind": "bumper", "pos": pygame.Vector2(335.5, 145), "radius": 23, "points": 100, "color": PINK, "flash": 0.0},
    {"kind": "star", "pos": pygame.Vector2(175.5, 250), "radius": 22, "points": 250, "color": YELLOW, "flash": 0.0},
    {"kind": "star", "pos": pygame.Vector2(305.5, 250), "radius": 22, "points": 250, "color": PINK, "flash": 0.0},
    {"kind": "bumper", "pos": pygame.Vector2(125.5, 355), "radius": 23, "points": 150, "color": CYAN, "flash": 0.0},
    {"kind": "bumper", "pos": pygame.Vector2(240.5, 355), "radius": 30, "points": 40, "color": CYAN, "flash": 0.0},
    {"kind": "bumper", "pos": pygame.Vector2(355.5, 355), "radius": 23, "points": 150, "color": YELLOW, "flash": 0.0},
    {"kind": "star", "pos": pygame.Vector2(155.5, 465), "radius": 22, "points": 250, "color": PINK, "flash": 0.0},
    {"kind": "star", "pos": pygame.Vector2(325.5, 465), "radius": 22, "points": 250, "color": YELLOW, "flash": 0.0},
]


def reset_ball():
    global phase, charge, charge_direction, space_held, ball_in_playfield
    global slingshots_active, moon_guide_stage, moon_guide_curve, moon_guide_progress
    BALL_POS.update(BALL_START)
    BALL_VELOCITY.update(0, 0)
    phase = "ready"
    charge = 0
    charge_direction = 1
    space_held = False
    ball_in_playfield = False
    slingshots_active = False
    moon_guide_stage = 0
    moon_guide_curve = ()
    moon_guide_progress = 0.0


def launch_ball():
    global phase, ball_in_playfield, slingshots_active, moon_guide_stage
    global moon_guide_curve, moon_guide_progress
    force = 10 + charge * 0.12
    BALL_POS.update(BALL_START)
    BALL_VELOCITY.update(0, -force)
    phase = "playing"
    ball_in_playfield = False
    slingshots_active = False
    moon_guide_stage = 1 if charge >= MAX_LAUNCH_GUIDE_CHARGE else 0
    moon_guide_curve = ()
    moon_guide_progress = 0.0


def build_moon_guide_curve():
    moon = next(target for target in targets if target["kind"] == "moon")
    outer_arc = moon_points(moon["pos"], moon["radius"])
    upper_tip = pygame.Vector2(outer_arc[0])
    outward = (upper_tip - moon["pos"]).normalize()
    endpoint = upper_tip - outward * (BALL_RADIUS - 1)
    return (
        BALL_POS.copy(),
        BALL_POS + BALL_VELOCITY * (MOON_GUIDE_DURATION / 3),
        pygame.Vector2(moon["pos"].x + 90, moon["pos"].y - 35),
        endpoint,
    )


def cubic_guide_point_and_tangent(control_points, progress):
    start, control_a, control_b, end = control_points
    inverse = 1 - progress
    position = (start * inverse ** 3
                + control_a * (3 * inverse ** 2 * progress)
                + control_b * (3 * inverse * progress ** 2)
                + end * progress ** 3)
    tangent = (3 * inverse ** 2 * (control_a - start)
               + 6 * inverse * progress * (control_b - control_a)
               + 3 * progress ** 2 * (end - control_b))
    return position, tangent


def collide_with_target(target):
    global score, BALL_VELOCITY
    if target["kind"] in ("star", "moon"):
        collide_with_polygon_target(target)
        return

    offset = BALL_POS - target["pos"]
    distance = offset.length()
    minimum_distance = BALL_RADIUS + target["radius"]
    if distance >= minimum_distance:
        return

    normal = offset.normalize() if distance else pygame.Vector2(0, -1)
    BALL_POS.update(target["pos"] + normal * (minimum_distance + 1))
    speed_toward_target = BALL_VELOCITY.dot(normal)
    if speed_toward_target < 0:
        BALL_VELOCITY -= 1.9 * speed_toward_target * normal
    BALL_VELOCITY += normal * 2.5
    target["flash"] = 1.0
    score += target["points"]


def closest_point_on_segment(point, start, end):
    segment = end - start
    length_squared = segment.length_squared()
    if not length_squared:
        return start
    fraction = max(0.0, min(1.0, (point - start).dot(segment) / length_squared))
    return start + segment * fraction


def point_in_polygon(point, vertices):
    inside = False
    previous = vertices[-1]
    for current in vertices:
        crosses_height = (current.y > point.y) != (previous.y > point.y)
        if crosses_height:
            crossing_x = ((previous.x - current.x) * (point.y - current.y)
                          / (previous.y - current.y) + current.x)
            if point.x < crossing_x:
                inside = not inside
        previous = current
    return inside


def collide_with_polygon_target(target):
    global score, BALL_VELOCITY, moon_guide_stage
    pulse = target["flash"]
    if target["kind"] == "star":
        outer_radius = target["radius"] + 5 + int(pulse * 6)
        shape_points = star_points(target["pos"], outer_radius,
                                   outer_radius * 0.43, pulse * 0.18)
    else:
        radius = target["radius"] + int(pulse * 4)
        shape_points = moon_points(target["pos"], radius)
    vertices = [pygame.Vector2(point) for point in shape_points]
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    nearest, edge_start, edge_end = min(
        ((closest_point_on_segment(BALL_POS, start, end), start, end)
         for start, end in edges),
        key=lambda result: BALL_POS.distance_squared_to(result[0]),
    )
    offset = BALL_POS - nearest
    distance = offset.length()
    inside = point_in_polygon(BALL_POS, vertices)
    if target["kind"] == "moon":
        radius = target["radius"] + int(pulse * 4)
        cutout_center = target["pos"] + pygame.Vector2(radius * 0.46, 0)
        cutout_radius = radius * 0.9
        if BALL_POS.distance_squared_to(cutout_center) < cutout_radius ** 2:
            return
    if not inside and distance >= BALL_RADIUS:
        return

    if distance > 1e-6:
        normal = -offset.normalize() if inside else offset.normalize()
    else:
        edge = edge_end - edge_start
        normal = pygame.Vector2(edge.y, -edge.x).normalize()
        midpoint = (edge_start + edge_end) / 2
        if point_in_polygon(midpoint + normal, vertices):
            normal = -normal

    BALL_POS.update(nearest + normal * (BALL_RADIUS + 1))
    speed_toward_shape = BALL_VELOCITY.dot(normal)
    if speed_toward_shape < 0:
        BALL_VELOCITY -= 1.9 * speed_toward_shape * normal
    BALL_VELOCITY += normal * 2.5
    target["flash"] = 1.0
    score += target["points"]
    if target["kind"] == "moon":
        moon_guide_stage = 0


def collide_with_flipper(start, end, extension):
    global BALL_VELOCITY
    nearest = closest_point_on_segment(BALL_POS, start, end)
    offset = BALL_POS - nearest
    distance = offset.length()
    flipper_radius = 9
    if distance >= BALL_RADIUS + flipper_radius:
        return

    normal = offset.normalize() if distance else pygame.Vector2(0, -1)
    BALL_POS.update(nearest + normal * (BALL_RADIUS + flipper_radius + 1))
    if extension > 0.1:
        lift = 7.0 + 5.5 * extension
        BALL_VELOCITY.y = min(BALL_VELOCITY.y, -lift)
        BALL_VELOCITY.x += (-2.2 if start.x < SCREEN_WIDTH / 2 else 2.2) * extension
    elif BALL_VELOCITY.dot(normal) < 0:
        BALL_VELOCITY -= 1.6 * BALL_VELOCITY.dot(normal) * normal


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def side_wall_limits(y, in_playfield):
    if not in_playfield:
        return PLAYFIELD_LEFT, SHOOTER_LANE_RIGHT
    if y >= TOP_ARCH_CENTER.y:
        return PLAYFIELD_LEFT, PLAYFIELD_RIGHT
    vertical_offset = y - TOP_ARCH_CENTER.y
    if abs(vertical_offset) >= TOP_ARCH_RADIUS:
        return TOP_ARCH_CENTER.x, TOP_ARCH_CENTER.x
    half_width = math.sqrt(TOP_ARCH_RADIUS ** 2 - vertical_offset ** 2)
    return TOP_ARCH_CENTER.x - half_width, TOP_ARCH_CENTER.x + half_width


def side_rail_points(left_side):
    x = PLAYFIELD_LEFT if left_side else PLAYFIELD_RIGHT
    return [(x, TOP_ARCH_CENTER.y), (x, BOTTOM_ARCH_CENTER.y)]


def flipper_segments(extension):
    eased_extension = smoothstep(extension)
    tips = []
    for index, pivot in enumerate(FLIPPER_PIVOTS):
        rest_vector = FLIPPER_REST_TIPS[index] - pivot
        active_vector = FLIPPER_ACTIVE_TIPS[index] - pivot
        rest_angle = math.atan2(rest_vector.y, rest_vector.x)
        active_angle = math.atan2(active_vector.y, active_vector.x)
        angle_delta = active_angle - rest_angle
        if index == 1:
            angle_delta = (angle_delta + math.pi) % (2 * math.pi) - math.pi
        length = rest_vector.length() * 1.15
        angle = rest_angle + angle_delta * eased_extension
        tips.append(pivot + pygame.Vector2(math.cos(angle), math.sin(angle)) * length)
    return tuple(zip(FLIPPER_PIVOTS, tips))


def top_rail_points():
    points = []
    for index in range(49):
        angle = math.pi + math.pi * index / 48
        points.append((TOP_ARCH_CENTER.x + TOP_ARCH_RADIUS * math.cos(angle),
                       TOP_ARCH_CENTER.y + TOP_ARCH_RADIUS * math.sin(angle)))
    return points


def bottom_rail_points():
    points = []
    for index in range(49):
        angle = math.pi * index / 48
        points.append((BOTTOM_ARCH_CENTER.x + BOTTOM_ARCH_RADIUS * math.cos(angle),
                       BOTTOM_ARCH_CENTER.y + BOTTOM_ARCH_RADIUS * math.sin(angle)))
    return points


def collide_with_top_wall():
    offset_x = BALL_POS.x - TOP_ARCH_CENTER.x
    if abs(offset_x) >= TOP_ARCH_INNER_RADIUS:
        return
    arc_height = math.sqrt(TOP_ARCH_INNER_RADIUS ** 2 - offset_x ** 2)
    minimum_y = TOP_ARCH_CENTER.y - arc_height
    if BALL_POS.y < minimum_y:
        BALL_POS.y = minimum_y
        BALL_VELOCITY.y = abs(BALL_VELOCITY.y) * 0.82


def collide_with_bottom_wall():
    global BALL_VELOCITY
    offset = BALL_POS - BOTTOM_ARCH_CENTER
    distance = offset.length()
    if BALL_POS.y <= BOTTOM_ARCH_CENTER.y or distance <= TOP_ARCH_INNER_RADIUS:
        return
    normal = offset.normalize()
    BALL_POS.update(BOTTOM_ARCH_CENTER + normal * TOP_ARCH_INNER_RADIUS)
    speed_into_wall = BALL_VELOCITY.dot(normal)
    if speed_into_wall > 0:
        BALL_VELOCITY -= 1.7 * speed_into_wall * normal


def collide_with_guide_rail(start, end):
    global BALL_VELOCITY
    nearest = closest_point_on_segment(BALL_POS, start, end)
    offset = BALL_POS - nearest
    distance = offset.length()
    bar_radius = 7
    if distance >= BALL_RADIUS + bar_radius:
        return
    normal = offset.normalize() if distance else pygame.Vector2(0, -1)
    BALL_POS.update(nearest + normal * (BALL_RADIUS + bar_radius + 1))
    speed_into_bar = BALL_VELOCITY.dot(normal)
    if speed_into_bar < 0:
        BALL_VELOCITY -= 1.7 * speed_into_bar * normal


def collide_with_triangle(vertices):
    global BALL_VELOCITY
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    nearest, edge_start, edge_end = min(
        ((closest_point_on_segment(BALL_POS, start, end), start, end)
         for start, end in edges),
        key=lambda result: BALL_POS.distance_squared_to(result[0]),
    )
    offset = BALL_POS - nearest
    inside = all(
        (end.x - start.x) * (BALL_POS.y - start.y)
        - (end.y - start.y) * (BALL_POS.x - start.x) >= 0
        for start, end in edges
    ) or all(
        (end.x - start.x) * (BALL_POS.y - start.y)
        - (end.y - start.y) * (BALL_POS.x - start.x) <= 0
        for start, end in edges
    )
    if not inside and offset.length_squared() >= (BALL_RADIUS + 4) ** 2:
        return

    if inside or offset.length_squared() == 0:
        edge = edge_end - edge_start
        normal = pygame.Vector2(edge.y, -edge.x).normalize()
        midpoint = (edge_start + edge_end) / 2
        center = sum(vertices, pygame.Vector2()) / len(vertices)
        if normal.dot(midpoint - center) < 0:
            normal = -normal
    else:
        normal = offset.normalize()

    BALL_POS.update(nearest + normal * (BALL_RADIUS + 4))
    speed_into_triangle = BALL_VELOCITY.dot(normal)
    if speed_into_triangle < 0:
        BALL_VELOCITY -= 1.7 * speed_into_triangle * normal


def run_game():
    global window, screen, clock
    global score, lives, phase, charge, charge_direction, space_held
    global ball_in_playfield, slingshots_active, moon_guide_stage
    global moon_guide_curve, moon_guide_progress, flipper_extension, BALL_POS

    window = pygame.display.set_mode((WINDOW_WIDTH, SCREEN_HEIGHT))
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pinball")
    clock = pygame.time.Clock()

    running = True
    while running:
        delta = min(clock.tick(FPS) / (1000 / FPS), 2.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if phase == "ready":
                    phase = "charging"
                    space_held = True
                elif phase == "game_over":
                    score = 0
                    lives = 3
                    for target in targets:
                        target["flash"] = 0
                    reset_ball()
                elif phase == "playing":
                    space_held = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                if phase == "charging":
                    launch_ball()
                space_held = False

        if phase == "charging":
            charge += charge_direction * 1.35 * delta
            if charge >= 100:
                charge = 100
                charge_direction = -1
            elif charge <= 0:
                charge = 0
                charge_direction = 1

        flipper_target = 1.0 if phase == "playing" and space_held else 0.0
        flipper_speed = FLIPPER_RAISE_SPEED if flipper_target > flipper_extension else FLIPPER_LOWER_SPEED
        extension_step = flipper_speed * delta
        if flipper_target > flipper_extension:
            flipper_extension = min(flipper_target, flipper_extension + extension_step)
        else:
            flipper_extension = max(flipper_target, flipper_extension - extension_step)

        if phase == "playing":
            if moon_guide_stage == 2:
                moon_guide_progress = min(
                    1.0, moon_guide_progress + delta / MOON_GUIDE_DURATION)
                guide_position, guide_tangent = cubic_guide_point_and_tangent(
                    moon_guide_curve, moon_guide_progress)
                BALL_POS.update(guide_position)
                BALL_VELOCITY.update(guide_tangent / MOON_GUIDE_DURATION)
                if moon_guide_progress >= 1.0:
                    moon_guide_stage = 0
            else:
                BALL_VELOCITY.y += GRAVITY * delta
                BALL_POS += BALL_VELOCITY * delta

                if (moon_guide_stage == 1 and BALL_VELOCITY.y < 0
                        and BALL_POS.y <= MAX_LAUNCH_GUIDE_Y):
                    moon_guide_curve = build_moon_guide_curve()
                    moon_guide_progress = 0.0
                    moon_guide_stage = 2

            if (not ball_in_playfield and BALL_VELOCITY.y < 0
                    and BALL_POS.y <= SLINGSHOT_ENTRY_Y):
                ball_in_playfield = True
            if (not slingshots_active and BALL_VELOCITY.y < 0
                    and BALL_POS.y <= SLINGSHOT_TOP_Y):
                slingshots_active = True

            if ball_in_playfield:
                left_wall, right_wall = side_wall_limits(BALL_POS.y, True)
                if BALL_POS.x < left_wall + BALL_RADIUS:
                    BALL_POS.x = left_wall + BALL_RADIUS
                    BALL_VELOCITY.x = abs(BALL_VELOCITY.x) * 0.82
                elif BALL_POS.x > right_wall - BALL_RADIUS:
                    BALL_POS.x = right_wall - BALL_RADIUS
                    if BALL_VELOCITY.y < 0 and BALL_POS.y < SHOOTER_EXIT_Y:
                        wall_below = side_wall_limits(BALL_POS.y + 1, True)[1]
                        wall_above = side_wall_limits(BALL_POS.y - 1, True)[1]
                        wall_slope = (wall_below - wall_above) / 2
                        BALL_VELOCITY.x = min(BALL_VELOCITY.x,
                                                  wall_slope * BALL_VELOCITY.y * 0.75)
                    else:
                        BALL_VELOCITY.x = -abs(BALL_VELOCITY.x) * 0.82
                collide_with_top_wall()
                collide_with_bottom_wall()
                if slingshots_active:
                    for triangle in SLINGSHOT_TRIANGLES:
                        collide_with_triangle(triangle)
                for guide_start, guide_end in FLIPPER_GUIDES:
                    collide_with_guide_rail(guide_start, guide_end)

                for target in targets:
                    collide_with_target(target)

                for start, end in flipper_segments(flipper_extension):
                    collide_with_flipper(start, end, flipper_extension)

            if BALL_POS.y > 716:
                lives -= 1
                if lives <= 0:
                    finish_game()
                else:
                    reset_ball()

        draw_table(screen, globals())
        window.fill(BLACK)
        content_offset = (WINDOW_WIDTH - (530 - 18)) // 2 - 18
        window.blit(screen, (content_offset, 0))
        pygame.display.flip()

    pygame.quit()