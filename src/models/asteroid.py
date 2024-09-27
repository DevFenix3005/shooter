from random import randint

from .game_sprite import GameSprite
from .table_score import TableScore
from constants import WIN_WIDTH, WIN_HEIGHT


# clase del objeto enemigo
class Asteroid(GameSprite):
    """
    Se va a mover como un enemigo
    Que no nos cuente como perdida
    Que no se pueda elimnar
    Nueva imagen para el asteroid
    Randomizador de velocidad
    """

    def __init__(
        self,
        player_image,
        player_x,
        player_y,
        size_x,
        size_y,
        player_speed,
    ):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)

    # movimiento del enemigo
    def update(self):
        self.rect.y += self.speed

        # desaparece si alcanza el borde de la pantalla
        if self.rect.y > WIN_HEIGHT:
            self.rect.x = randint(80, WIN_WIDTH - 80)
            self.rect.y = 0
