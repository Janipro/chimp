# ----------------------------------------------------------------------
# This is me learning the "simple" chimp game, made to get more familiar
# with both the pygame module and python in general. Feel free to
# implement this project in your own way! Made with pygame.
# ----------------------------------------------------------------------


import os
import pygame
from pygame.locals import *

# Checking to see if some of the optional modules are available
if not pygame.font:
    print("Fonts have not been initialized!!")
if not pygame.mixer:
    print("Sounds have not been initialized!!")


def load_image(name, color_key=None):
    fullname = os.path.join("main", name)  # Universal path that works everywhere
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image: ", name)
        raise SystemExit(message)
    image = image.convert()
    if color_key is not None:
        if color_key == -1:  # This will grab the topleft pixel of the image
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:  # A dummy method for catching errors without doing a lot of work
        def play(self): pass

    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join("main", name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print("Cannot load sound: ", name)
        raise SystemExit(message)
    return sound


# Sprite is a module with basic game objects
class Fist(pygame.sprite.Sprite):
    """moves an emoji fist on the screen, tracing the mouse movement"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # Initialize the sprite module
        self.image, self.rect = load_image("fist.png", -1)
        self.punching = 0

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)  # Check to see if the fist is hitting the target

    def unpunch(self):
        self.punching = 0  # Used to remove fist


class Chimp(pygame.sprite.Sprite):
    """This is our moving monkey, which will spin when punched"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("monkey.png", -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 12
        self.dizzy = 0

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        new_position = self.rect.move((self.move, 0))
        if new_position not in self.area:
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.move = -self.move
                new_position = self.rect.move((self.move, 0))
                self.image = pygame.transform.flip(self.image, 1, 0)
            self.rect = new_position

    def _spin(self):
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image  # A copy of the current image


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Apetrøbbel!")
    pygame.mouse.set_visible(False)
    background = pygame.Surface(screen.get_size())
    background = background.convert()  # Size window to display
    background.fill((250, 250, 250))

    if pygame.font:  # Check to see if font has been imported
        font = pygame.font.Font(None, 36)
        text = font.render("Treff apen!", 1, (10, 10, 10))
        text_position = text.get_rect(centerx=background.get_width() // 2)  # Centered position is half of width
        background.blit(text, text_position)  # Blit means paste

    screen.blit(background, (0, 0))
    pygame.display.flip()
    whiff_sound = load_sound("whiff.wav")
    punch_sound = load_sound("punch.wav")
    chimp = Chimp()
    fist = Fist()
    all_sprites = pygame.sprite.RenderPlain((fist, chimp))
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if fist.punch(chimp):
                    punch_sound.play()
                    chimp.punched()
                else:
                    whiff_sound.play()
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()

        all_sprites.update()
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()


main()  # Run our program
