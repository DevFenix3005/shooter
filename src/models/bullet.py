from .game_sprite import GameSprite


# clase del objeto de la bala
class Bullet(GameSprite):
    # movimiento del enemigo
    def update(self):
        self.rect.y += self.speed
        # desaparece si alcanza el borde de la pantalla
        if self.rect.y < 0:
            self.kill()
