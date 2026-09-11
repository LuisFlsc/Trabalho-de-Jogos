from util import circle_collistiion, EventHandler
from bullet import PlayerBullet, EnemyBullet
from enemy import Enemy


def resolve_combat(objects, player):
    """Verifica colisões de balas contra inimigos/jogador. Roda uma vez por frame."""

    player_bullets = [o for o in objects if isinstance(o, PlayerBullet) and o.alive]
    enemy_bullets = [o for o in objects if isinstance(o, EnemyBullet) and o.alive]
    enemies = [o for o in objects if isinstance(o, Enemy) and o.alive]

    # balas do jogador -> inimigos
    for bullet in player_bullets:
        for enemy in enemies:
            if not enemy.alive or id(enemy) in bullet.hit_enemies:
                continue
            if circle_collistiion(bullet.pos, bullet.radius, enemy.pos, enemy.radius):
                enemy.take_damage(bullet.damage)
                bullet.hit_enemies.add(id(enemy))
                if bullet.pierce <= 0:
                    bullet.destroy()
                else:
                    bullet.pierce -= 1
                break

    # balas de inimigos -> jogador
    for bullet in enemy_bullets:
        if circle_collistiion(bullet.pos, bullet.radius, player.pos, 16):
            EventHandler().notify("DamagePlayer", {"amount": bullet.damage, "magic": False})
            bullet.destroy()
