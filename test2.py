import os
import pygame

pygame.init()
size = width, height = WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()


def load_image(name, per_pixel_alpha=False, color_key=None):
    fullname = os.path.join('data', 'textures', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if per_pixel_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    return image


bI = pygame.transform.scale(load_image('player\\player1_south.png', True), (256, 256))
bI_rect = bI.get_rect()

base = load_image('test_textures\\base1_sheet.png', True)
base_rect = base.get_rect()
jacket = load_image('test_textures\\jacket1_sheet.png', True)
jacket_rect = jacket.get_rect()
pants = load_image('test_textures\\pants1_sheet.png', True)
pants_rect = pants.get_rect()
boots = load_image('test_textures\\boots1_sheet.png', True)
boots_rect = boots.get_rect()
hat = load_image('test_textures\\hat1_sheet.png', True)
hat_rect = hat.get_rect()

player_image = pygame.Surface((base_rect.width, base_rect.height))
player_image.fill('#CDECDC')
player_image.blit(base, (0, 0))
player_image.blit(hat, (0, 0))
player_image.blit(jacket, (0, 0))
player_image.blit(pants, (0, 0))
player_image.blit(boots, (0, 0))

pygame.image.save(player_image, 'data\\textures\\test_textures\\output_image1.png')

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(pygame.Color("#AAAAAA"))

    # screen.blit(base, (300, 100))
    # screen.blit(hat, (300, 88))
    # screen.blit(jacket, (300, 148))
    # screen.blit(pants, (300, 148 + jacket_rect.height))
    # screen.blit(boots, (300, 148 + jacket_rect.height + pants_rect.height))

    screen.blit(player_image, (0, 0))

    # screen.blit(bI, (300, 116))

    all_sprites.draw(screen)
    all_sprites.update(keys=keys)

    pygame.display.flip()
    clock.tick(FPS)
