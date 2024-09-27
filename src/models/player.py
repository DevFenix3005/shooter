from pygame import key, K_UP, K_DOWN, K_LEFT, K_RIGHT
from .game_sprite import GameSprite
from .bullet import Bullet
from constants import WIN_WIDTH, WIN_HEIGHT, IMG_BULLET


# clase de jugador principal
class Player(GameSprite):
    def __init__(
        self, player_image, player_x, player_y, size_x, size_y, player_speed, bullets
    ):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.__bullets = bullets

    # método para controlar el objeto con las flechas del teclado
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed

        if keys[K_RIGHT] and self.rect.x < WIN_WIDTH - 80:
            self.rect.x += self.speed

        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed

        if keys[K_DOWN] and self.rect.y < WIN_HEIGHT - 100:
            self.rect.y += self.speed

    # el método “disparo” (usamos la posición del jugador para crear una bala)
    def fire(self):
        bullet = Bullet(IMG_BULLET, self.rect.centerx, self.rect.top, 15, 20, -15)
        self.__bullets.add(bullet)
