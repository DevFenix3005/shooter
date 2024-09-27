from pygame import (
    init,
    quit,
    display,
    transform,
    mixer,
    image,
    sprite,
    event,
    font as _font,
    time,
    QUIT,
    KEYDOWN,
    K_SPACE,
    K_RETURN,
    Rect,
    draw,
)
from random import randint
from models import Enemy, Player, TableScore, Asteroid, Explosion
from constants import (
    WIN_WIDTH,
    WIN_HEIGHT,
    IMG_BACK,
    IMG_HERO,
    IMG_ENEMY,
    IMG_ENEMY_LVL3,
    IMG_WIN,
    IMG_LOS,
    IMG_ASTEROID,
    SHOT_DELAY,
)

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)


# Función genérica para crear objetos como monstruos o asteroides
def create_asteroid(group, num_objects) -> None:
    for _ in range(num_objects):
        asteroid = Asteroid(
            IMG_ASTEROID, randint(80, WIN_WIDTH - 80), -40, 80, 50, randint(1, 5)
        )
        group.add(asteroid)


# Función genérica para crear objetos como monstruos o asteroides
def create_ufo(group, num_objects, table_score: TableScore = None) -> None:
    lvl = 3 if (table_score.score // 10) >= 3 else 1
    speed: tuple = (1, 3) if lvl == 3 else (1, 5)

    for _ in range(num_objects):
        enemy = Enemy(
            IMG_ENEMY_LVL3 if lvl == 3 else IMG_ENEMY,
            randint(80, WIN_WIDTH - 80),
            -40,
            80,
            50,
            randint(speed[0], speed[1]),
            lvl,
            lvl,
            table_score,
        )
        group.add(enemy)


def setup() -> None:
    global \
        font, \
        clock, \
        window, \
        background, \
        table_score, \
        bullets, \
        monsters, \
        asteroids, \
        explosions, \
        ship, \
        finish, \
        run, \
        last_shot_time

    # Configuramos el control de FPS
    _font.init()
    mixer.init()
    mixer.music.load("./assets/Attack.mp3")
    mixer.music.play()
    mixer.music.set_volume(0.2)
    font = _font.Font(None, 36)
    clock = time.Clock()

    display.set_caption("SpaceGunner")
    window = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    background = transform.scale(image.load(IMG_BACK), (WIN_WIDTH, WIN_HEIGHT))

    table_score = TableScore()

    # Creando un grupo de objetos
    bullets = sprite.Group()
    monsters = sprite.Group()
    asteroids = sprite.Group()
    explosions = sprite.Group()

    # Creando objetos
    ship = Player(IMG_HERO, 5, WIN_HEIGHT - 100, 80, 100, 10, bullets)
    create_ufo(monsters, 5, table_score)
    create_asteroid(asteroids, 3)

    finish = False
    run = True  # La bandera se restablece usando el botón de cerrar ventana
    last_shot_time = 0  # Para controlar el delay entre disparos


def controller() -> None:
    global run, last_shot_time

    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and not finish:
                current_time = time.get_ticks()
                if current_time - last_shot_time > SHOT_DELAY:  # Control de disparo
                    ship.fire()
                    last_shot_time = current_time
            elif e.key == K_RETURN and finish:  # Reiniciar el juego
                setup()


def draw_health_bar(enemy, window):
    # Tamaño de la barra de salud
    bar_width = 50
    bar_height = 10
    fill = (enemy.health / enemy.max_health) * bar_width  # Proporción de salud restante
    outline_rect = Rect(enemy.rect.x, enemy.rect.y - 10, bar_width, bar_height)
    fill_rect = Rect(enemy.rect.x, enemy.rect.y - 10, fill, bar_height)

    draw.rect(window, (255, 0, 0), fill_rect)  # Barra roja (salud)
    draw.rect(window, (255, 255, 255), outline_rect, 2)  # Contorno de la barra


def draw_sprites():
    # Actualizando objetos
    ship.update()
    monsters.update()
    asteroids.update()
    bullets.update()
    explosions.update()

    ship.reset(window)
    monsters.draw(window)
    bullets.draw(window)
    asteroids.draw(window)
    explosions.draw(window)

    for enemy in monsters:
        draw_health_bar(enemy, window)


def loop() -> None:
    global finish

    controller()

    if not finish:
        # Actualizando el fondo
        window.blit(background, (0, 0))

        # Escribiendo texto en la pantalla
        text = font.render("Puntaje: " + str(table_score.score), 1, WHITE)
        window.blit(text, (10, 20))

        text_lose = font.render("Falló: " + str(table_score.lost), 1, WHITE)
        window.blit(text_lose, (10, 50))

        draw_sprites()

        # Comprobación de colisión de bala-monstruo
        collides = sprite.groupcollide(monsters, bullets, False, True, sprite.collide_mask)
        for monster, hit_bullets in collides.items():
            for _ in hit_bullets:
                monster.health -= 1

            if monster.health <= 0:
                table_score.score += 1
                # Crear nuevos enemigos cuando se eliminan
                create_ufo(monsters, 1, table_score)

                explosion = Explosion(monster.rect.centerx, monster.rect.centery)
                explosions.add(explosion)
                monster.kill()  # Elimina al enemigo del grupo

        # Posible derrota
        if (
            sprite.spritecollide(ship, monsters, False, sprite.collide_mask)
            or sprite.spritecollide(ship, asteroids, False, sprite.collide_mask)
            or table_score.lost >= table_score.max_lost
        ):
            finish = True
            img = image.load(IMG_LOS)
            d = img.get_width() // img.get_height()
            window.fill(WHITE)
            window.blit(transform.scale(img, (WIN_HEIGHT * d, WIN_HEIGHT)), (90, 0))

        # Comprobación de victoria
        if table_score.score >= table_score.goal:
            finish = True
            img = image.load(IMG_WIN)
            window.fill(WHITE)
            window.blit(transform.scale(img, (WIN_WIDTH, WIN_HEIGHT)), (0, 0))
    else:
        text_restart = font.render("El juego ha terminado.", 1, RED)
        window.blit(text_restart, (WIN_WIDTH // 4, WIN_HEIGHT // 2))
        text_restart = font.render("Presiona ENTER para reiniciar.", 1, RED)
        window.blit(text_restart, (WIN_WIDTH // 4, (WIN_HEIGHT // 2) + 25))
        display.update()

    display.update()
    clock.tick(30)  # Controlamos el juego a 30 FPS


def start_game():
    init()
    setup()
    while run:
        loop()
    quit()


if __name__ == "__main__":
    start_game()
