from pygame import sprite, transform, image


class Explosion(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []  # Aquí puedes agregar varias imágenes para la animación
        for i in range(1, 5):  # Supongamos que tienes 5 frames de animación
            img = transform.scale(
                image.load(f"./assets/explosion/explosion{i}.png"), (80, 80)
            )
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 5  # Velocidad de cambio entre frames
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index += 1
            if self.index < len(self.images):
                self.image = self.images[self.index]
            else:
                self.kill()  # Termina la animación y elimina el sprite
