import pygame
from player import Player
from wave_manager import WaveManager
from upgrades import generate_choices
from shop import generate_shop
from util import EventHandler, draw_text
from combat import resolve_combat
import ui

# inicialização

pygame.init()
WIDTH, HEIGHT = 1280, 720
clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survivor-like")

objects = []
player = Player((WIDTH // 2, HEIGHT // 2), objects_ref=objects)
objects.append(player)

wave_manager = WaveManager(player)

STATE_PLAYING = "playing"
STATE_LEVELUP = "levelup"
STATE_SHOP = "shop"
STATE_GAMEOVER = "gameover"

game = {
    "state": STATE_PLAYING,
    "pending_upgrades": [],
    "shop_items": [],
}


# funções auxiliares (inscritas nos eventos, no mesmo espírito do EventHandler já usado)

def remove_obj(obj):
    if obj in objects:
        objects.remove(obj)


def spawn_obj(obj):
    objects.append(obj)


def on_add_xp(amount):
    if game["state"] != STATE_PLAYING:
        return
    leveled = player.stats.add_xp(amount + player.stats.xp_bonus)
    if leveled:
        game["pending_upgrades"] = generate_choices(3)
        game["state"] = STATE_LEVELUP


def on_add_coin(amount):
    player.stats.add_coins(amount + player.stats.gold_bonus)


def on_wave_cleared(wave_number):
    game["shop_items"] = generate_shop(wave_number)
    game["state"] = STATE_SHOP


EventHandler().subscribe("DestroyObj", remove_obj)
EventHandler().subscribe("SpawnObject", spawn_obj)
EventHandler().subscribe("AddXP", on_add_xp)
EventHandler().subscribe("AddCoin", on_add_coin)
EventHandler().subscribe("WaveCleared", on_wave_cleared)

wave_manager.start_next_wave()


# entrada por estado

def handle_playing_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.action_1()          # dash
            if event.key == pygame.K_TAB:
                player.action_2()          # bola de fogo
            if event.key == pygame.K_q:
                player.action_3()          # raio em cadeia
            if event.key == pygame.K_e:
                player.action_4(pygame.mouse.get_pos())  # nevasca em cone
            if event.key == pygame.K_r:
                player.action_5()          # campo de força
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # botão direito
                player.cast_basic_spell(pygame.mouse.get_pos())


def choose_upgrade(index):
    if index >= len(game["pending_upgrades"]):
        return
    upgrade = game["pending_upgrades"][index]
    upgrade.apply(player.stats)
    game["pending_upgrades"] = []
    game["state"] = STATE_PLAYING


def handle_levelup_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            for i in range(len(game["pending_upgrades"])):
                if event.key == pygame.K_1 + i:
                    choose_upgrade(i)


def close_shop():
    game["shop_items"] = []
    game["state"] = STATE_PLAYING
    wave_manager.start_next_wave()


def handle_shop_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                close_shop()
            else:
                for i in range(len(game["shop_items"])):
                    if event.key == pygame.K_1 + i:
                        game["shop_items"][i].buy(player)


def handle_gameover_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


# loop principal

running = True
while running:

    if game["state"] == STATE_PLAYING:
        handle_playing_input()

        for obj in list(objects):
            obj.update(1)

        resolve_combat(objects, player)
        wave_manager.update(1, (WIDTH, HEIGHT))

        if player.stats.is_dead():
            game["state"] = STATE_GAMEOVER

    elif game["state"] == STATE_LEVELUP:
        handle_levelup_input()

    elif game["state"] == STATE_SHOP:
        handle_shop_input()

    elif game["state"] == STATE_GAMEOVER:
        handle_gameover_input()

    # desenho

    screen.fill((30, 30, 30))

    for obj in objects:
        obj.draw(screen)

    ui.draw_hud(screen, player, wave_manager, objects)

    if game["state"] == STATE_LEVELUP:
        ui.draw_level_up(screen, game["pending_upgrades"])
    elif game["state"] == STATE_SHOP:
        ui.draw_shop(screen, game["shop_items"], player.stats.coins)
    elif game["state"] == STATE_GAMEOVER:
        ui.draw_game_over(screen, wave_manager.wave)

    pygame.display.flip()
    clock.tick(60)
