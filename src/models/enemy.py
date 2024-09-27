from random import randint

from .game_sprite import GameSprite
from .table_score import TableScore
from constants import WIN_WIDTH, WIN_HEIGHT


# clase del objeto enemigo
class Enemy(GameSprite):
    __table_score: TableScore
    __health: int

    def __init__(
        self,
        player_image,
        player_x,
        player_y,
        size_x,
        size_y,
        player_speed,
        health,
        max_health,
        table_score: TableScore,
    ):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.__table_score = table_score
        self.__health = health
        self.__max_health = max_health

    # movimiento del enemigo
    def update(self):
        self.rect.y += self.speed

        # desaparece si alcanza el borde de la pantalla
        if self.rect.y > WIN_HEIGHT:
            self.rect.x = randint(80, WIN_WIDTH - 80)
            self.rect.y = 0
            self.update_lost()

    def update_lost(self):
        current_lost = self.__table_score.lost
        self.__table_score.lost = current_lost + 1

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, value):
        self.__health = value

    @property
    def max_health(self):
        return self.__max_health
