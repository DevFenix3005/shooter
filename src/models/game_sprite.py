from pygame import sprite, transform, image, mask


# clase padre para otros objetos
class GameSprite(sprite.Sprite):
    # constructor de clase
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # llamando al constructor de clase (Sprite):
        sprite.Sprite.__init__(self)

        # cada objeto debe almacenar una propiedad image
        # image_load =
        #
        self.image = transform.scale(
            image.load(player_image).convert_alpha(), (size_x, size_y)
        )
        self.speed = player_speed

        # cada objeto debe almacenar la propiedad rect en la cual está inscrita
        self.rect = self.image.get_rect(center=(size_x // 2, size_y // 2))
        self.mask = mask.from_surface(self.image)
        self.rect.x = player_x
        self.rect.y = player_y

    # método que dibuja al personaje en la ventana
    def reset(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))
