from enum import Enum
from pathlib import Path
from random import randint
from tempfile import gettempdir

from pygame import (
    KEYDOWN,
    K_ESCAPE,
    K_p,
    K_RETURN,
    K_SPACE,
    QUIT,
    Rect,
    display,
    draw,
    event,
    font as _font,
    image,
    init,
    mixer,
    quit,
    sprite,
    Surface,
    SRCALPHA,
    time,
    transform,
)

from constants import (
    IMG_ASTEROID,
    IMG_BACK,
    IMG_ENEMY,
    IMG_ENEMY_LVL3,
    IMG_HERO,
    IMG_LOS,
    IMG_WIN,
    SHOT_DELAY,
    WIN_HEIGHT,
    WIN_WIDTH,
)
from models import Asteroid, Enemy, Explosion, Player, TableScore

WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 209, 102)


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    WIN = "win"
    LOSE = "lose"



def generate_theme_assets() -> dict[str, str]:
    theme_dir = Path(gettempdir()) / "kirby_broco_theme"
    theme_dir.mkdir(parents=True, exist_ok=True)

    def save(surface, filename: str) -> str:
        file_path = theme_dir / filename
        image.save(surface, file_path)
        return str(file_path)

    # Kirby con brócoli
    kirby = image.load(IMG_HERO).convert_alpha()
    kirby = transform.scale(kirby, (128, 128))
    draw.circle(kirby, (42, 140, 60), (108, 64), 16)
    draw.rect(kirby, (138, 90, 55), Rect(96, 58, 14, 12))

    # Proyectil de brócoli
    broccoli = Surface((64, 64), SRCALPHA)
    draw.rect(broccoli, (140, 94, 60), Rect(26, 36, 12, 22))
    draw.circle(broccoli, (55, 170, 76), (24, 26), 10)
    draw.circle(broccoli, (55, 170, 76), (34, 20), 11)
    draw.circle(broccoli, (55, 170, 76), (42, 28), 9)

    # Comida chatarra
    burger = Surface((128, 128), sprite.SRCALPHA)
    draw.ellipse(burger, (240, 175, 75), Rect(22, 24, 84, 26))
    draw.rect(burger, (120, 75, 45), Rect(20, 48, 88, 18))
    draw.rect(burger, (95, 180, 70), Rect(24, 64, 80, 8))
    draw.rect(burger, (255, 210, 95), Rect(20, 72, 88, 14))
    draw.ellipse(burger, (230, 160, 65), Rect(22, 84, 84, 26))

    fries = Surface((128, 128), SRCALPHA)
    draw.rect(fries, (210, 30, 30), Rect(30, 34, 68, 72), border_radius=12)
    for x in range(36, 95, 10):
        draw.rect(fries, (248, 210, 92), Rect(x, 20, 8, 30))

    donut = Surface((128, 128), SRCALPHA)
    draw.circle(donut, (232, 174, 116), (64, 64), 42)
    draw.circle(donut, (180, 120, 70), (64, 64), 20)

    # Fondo candy
    background = Surface((WIN_WIDTH, WIN_HEIGHT))
    for y in range(WIN_HEIGHT):
        color = (min(255, 30 + y // 6), min(255, 20 + y // 5), min(255, 70 + y // 8))
        draw.line(background, color, (0, y), (WIN_WIDTH, y))

    return {
        "hero": save(kirby, "kirby.png"),
        "bullet": save(broccoli, "broccoli_bullet.png"),
        "enemy": save(burger, "junk_food_burger.png"),
        "enemy_lvl3": save(fries, "junk_food_fries.png"),
        "asteroid": save(donut, "junk_food_donut.png"),
        "background": save(background, "candy_sky.png"),
    }


def create_asteroid(group, num_objects) -> None:
    for _ in range(num_objects):
        asteroid = Asteroid(
            IMG_ASTEROID, randint(80, WIN_WIDTH - 80), -40, 80, 50, randint(1, 5)
        )
        group.add(asteroid)


def create_ufo(group, num_objects, table_score: TableScore) -> None:
    lvl = 3 if (table_score.score // 10) >= 3 else 1
    speed: tuple[int, int] = (1, 3) if lvl == 3 else (1, 5)

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
    global font
    global small_font
    global clock
    global window
    global background
    global win_background
    global lose_background
    global table_score
    global bullets
    global monsters
    global asteroids
    global explosions
    global ship
    global run
    global last_shot_time
    global game_state
    global assets
    global IMG_ASTEROID
    global IMG_BACK
    global IMG_ENEMY
    global IMG_ENEMY_LVL3
    global IMG_HERO
    global generated_bullet_image

    _font.init()
    mixer.init()

    display.set_caption("Kirby Broco Blaster")
    window = display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    theme_assets = generate_theme_assets()
    IMG_BACK = theme_assets["background"]
    IMG_HERO = theme_assets["hero"]
    IMG_ENEMY = theme_assets["enemy"]
    IMG_ENEMY_LVL3 = theme_assets["enemy_lvl3"]
    IMG_ASTEROID = theme_assets["asteroid"]
    generated_bullet_image = theme_assets["bullet"]

    assets = {
        "music": "./assets/Attack.mp3",
        "background": transform.scale(image.load(IMG_BACK), (WIN_WIDTH, WIN_HEIGHT)),
        "win": transform.scale(image.load(IMG_WIN), (WIN_WIDTH, WIN_HEIGHT)),
    }

    lose_image = image.load(IMG_LOS)
    lose_ratio = lose_image.get_width() // max(1, lose_image.get_height())
    assets["lose"] = transform.scale(lose_image, (WIN_HEIGHT * lose_ratio, WIN_HEIGHT))

    background = assets["background"]
    win_background = assets["win"]
    lose_background = assets["lose"]

    mixer.music.load(assets["music"])
    mixer.music.play(-1)
    mixer.music.set_volume(0.2)

    font = _font.Font(None, 36)
    small_font = _font.Font(None, 28)
    clock = time.Clock()

    table_score = TableScore()

    bullets = sprite.Group()
    monsters = sprite.Group()
    asteroids = sprite.Group()
    explosions = sprite.Group()

    ship = Player(
        IMG_HERO,
        5,
        WIN_HEIGHT - 100,
        80,
        100,
        10,
        bullets,
        bullet_image=generated_bullet_image,
    )
    create_ufo(monsters, 5, table_score)
    create_asteroid(asteroids, 3)

    run = True
    game_state = GameState.MENU
    last_shot_time = 0


def draw_health_bar(enemy, surface):
    bar_width = 50
    bar_height = 10
    fill = (enemy.health / enemy.max_health) * bar_width
    outline_rect = Rect(enemy.rect.x, enemy.rect.y - 10, bar_width, bar_height)
    fill_rect = Rect(enemy.rect.x, enemy.rect.y - 10, fill, bar_height)

    draw.rect(surface, (255, 0, 0), fill_rect)
    draw.rect(surface, (255, 255, 255), outline_rect, 2)


def draw_sprites() -> None:
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


def draw_hud() -> None:
    score_text = font.render(f"Puntaje: {table_score.score}", True, WHITE)
    lose_text = font.render(f"Falló: {table_score.lost}/{table_score.max_lost}", True, WHITE)
    level = 3 if (table_score.score // 10) >= 3 else 1
    level_text = small_font.render(f"Nivel de comida chatarra: {level}", True, YELLOW)
    help_text = small_font.render("ESPACIO: disparar | P: pausar", True, WHITE)

    window.blit(score_text, (10, 15))
    window.blit(lose_text, (10, 45))
    window.blit(level_text, (10, 78))
    window.blit(help_text, (10, WIN_HEIGHT - 30))


def draw_menu() -> None:
    window.blit(background, (0, 0))
    title = font.render("Kirby Broco Blaster", True, WHITE)
    subtitle = small_font.render("ENTER para jugar", True, YELLOW)
    controls = small_font.render("Flechas para mover, ESPACIO para disparar", True, WHITE)

    window.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, WIN_HEIGHT // 2 - 60))
    window.blit(
        subtitle,
        (WIN_WIDTH // 2 - subtitle.get_width() // 2, WIN_HEIGHT // 2 - 20),
    )
    window.blit(
        controls,
        (WIN_WIDTH // 2 - controls.get_width() // 2, WIN_HEIGHT // 2 + 20),
    )


def draw_pause() -> None:
    pause_text = font.render("PAUSA", True, YELLOW)
    helper = small_font.render("Presiona P para continuar", True, WHITE)

    window.blit(pause_text, (WIN_WIDTH // 2 - pause_text.get_width() // 2, WIN_HEIGHT // 2 - 20))
    window.blit(helper, (WIN_WIDTH // 2 - helper.get_width() // 2, WIN_HEIGHT // 2 + 20))


def reset_match() -> None:
    global table_score
    global bullets
    global monsters
    global asteroids
    global explosions
    global ship
    global game_state
    global last_shot_time

    table_score = TableScore()
    bullets.empty()
    monsters.empty()
    asteroids.empty()
    explosions.empty()

    ship = Player(
        IMG_HERO,
        5,
        WIN_HEIGHT - 100,
        80,
        100,
        10,
        bullets,
        bullet_image=generated_bullet_image,
    )
    create_ufo(monsters, 5, table_score)
    create_asteroid(asteroids, 3)
    game_state = GameState.PLAYING
    last_shot_time = 0


def controller() -> None:
    global run
    global last_shot_time
    global game_state

    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                run = False
            elif game_state == GameState.MENU and e.key == K_RETURN:
                reset_match()
            elif game_state in {GameState.WIN, GameState.LOSE} and e.key == K_RETURN:
                game_state = GameState.MENU
            elif game_state == GameState.PLAYING and e.key == K_p:
                game_state = GameState.PAUSED
            elif game_state == GameState.PAUSED and e.key == K_p:
                game_state = GameState.PLAYING
            elif game_state == GameState.PLAYING and e.key == K_SPACE:
                current_time = time.get_ticks()
                if current_time - last_shot_time > SHOT_DELAY:
                    ship.fire()
                    last_shot_time = current_time


def loop() -> None:
    global game_state

    controller()

    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.PLAYING:
        window.blit(background, (0, 0))

        draw_sprites()
        draw_hud()

        collides = sprite.groupcollide(monsters, bullets, False, True, sprite.collide_mask)
        for monster, hit_bullets in collides.items():
            for _ in hit_bullets:
                monster.health -= 1

            if monster.health <= 0:
                table_score.score += 1
                create_ufo(monsters, 1, table_score)
                explosion = Explosion(monster.rect.centerx, monster.rect.centery)
                explosions.add(explosion)
                monster.kill()

        if (
            sprite.spritecollide(ship, monsters, False, sprite.collide_mask)
            or sprite.spritecollide(ship, asteroids, False, sprite.collide_mask)
            or table_score.lost >= table_score.max_lost
        ):
            game_state = GameState.LOSE

        if table_score.score >= table_score.goal:
            game_state = GameState.WIN
    elif game_state == GameState.PAUSED:
        window.blit(background, (0, 0))
        ship.reset(window)
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)
        explosions.draw(window)
        draw_hud()
        draw_pause()
    elif game_state == GameState.LOSE:
        window.fill(WHITE)
        window.blit(lose_background, (90, 0))
        text_restart = font.render("Derrota. ENTER para volver al menú", True, RED)
        window.blit(text_restart, (WIN_WIDTH // 2 - text_restart.get_width() // 2, 20))
    elif game_state == GameState.WIN:
        window.blit(win_background, (0, 0))
        text_restart = font.render("¡Victoria! ENTER para volver al menú", True, RED)
        window.blit(text_restart, (WIN_WIDTH // 2 - text_restart.get_width() // 2, 20))

    display.update()
    clock.tick(30)


def start_game() -> None:
    init()
    setup()
    while run:
        loop()
    quit()


if __name__ == "__main__":
    start_game()
