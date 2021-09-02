import pygame
import random
from pygame._sdl2.video import Window
import math
import time
import os
import sys

import win32api
import win32con
import win32gui
import win32com.client
from ctypes import windll
import webbrowser

screen_width = 350
screen_height = 350

FPS = 60
clock = pygame.time.Clock()

pygame.init()
window_width = pygame.display.Info().current_w
window_height = pygame.display.Info().current_h

screen_x = window_width // 2 - 300
screen_y = window_height // 2 - 300

os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (screen_x, screen_y)

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption('A Very Normal Game about a Bee')

hwnd = pygame.display.get_wm_info()['window']
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 128), 0, win32con.LWA_COLORKEY)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # python bundle
    pass
    asset_path = os.path.join(sys._MEIPASS, 'assets')
else:
    # normal python process
    asset_path = 'assets'

FONT_PATH = os.path.join(asset_path, 'fonts', 'EightBit Atari-Ascprin.ttf')
IMAGE_PATH = os.path.join(asset_path, 'images', 'bee1.png')
SOUND_PATH = os.path.join(asset_path, 'sounds', 'awesomeness.ogg')


class Text:
    def __init__(self, msg, x=250, y=250, size=50, blink=False, centered=False):
        self.msg = msg
        self.x = x
        self.y = y
        self.size = size
        self.blink = blink
        self.blink_timer = time.time()
        self.visible = True
        self.centered = centered

    def draw(self):
        if self.blink:
            if time.time() - self.blink_timer >= 0.5:
                self.blink_timer = time.time()
                self.visible = not self.visible
        if self.visible:
            text_font = pygame.font.Font(FONT_PATH, self.size)
            text = text_font.render(self.msg, False, (255, 255, 255))
            if self.centered:
                screen.blit(text, text.get_rect(center=(self.x, self.y)))
            else:
                screen.blit(text, text.get_rect(topleft=(self.x, self.y)))


class Hyperlink:
    def __init__(self, msg, x=250, y=250, size=50, centered=False, link='', inactive_color=(255, 255, 255), active_color=(0, 0, 255)):
        self.msg = msg
        self.x = x
        self.y = y
        self.size = size
        self.blink_timer = time.time()
        self.ic = inactive_color
        self.ac = active_color
        self.link = link
        self.centered = centered
        self.text = pygame.font.Font(FONT_PATH, self.size).render(self.msg, False, inactive_color)
        self.rect = screen.blit(self.text, self.text.get_rect(center=(self.x, self.y))) if self.centered else screen.blit(self.text, self.text.get_rect(topleft=(self.x, self.y)))

    def draw(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if self.rect.collidepoint(mx, my):
                        if self.link != '':
                            try:
                                webbrowser.open(self.link)
                            except webbrowser.Error:
                                print('An Error occurred while attempting to open link')
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            color = self.ac
        else:
            color = self.ic
        self.text = pygame.font.Font(FONT_PATH, self.size).render(self.msg, False, color)
        self.rect = screen.blit(self.text, self.text.get_rect(center=(self.x, self.y))) if self.centered else screen.blit(self.text, self.text.get_rect(topleft=(self.x, self.y)))

        pygame.draw.line(screen, color, (self.rect.left, self.rect.bottom + 1), (self.rect.right, self.rect.bottom + 1), 2)


class SpriteSheet:
    def __init__(self, img_file_name, sprite_qty, row, col, color_key=None, flipped=False, scale_factor=1):
        self.scale_factor = scale_factor
        self.is_flipped = flipped
        self.sheet = pygame.image.load(img_file_name)
        self.row = row
        self.col = col
        self.w = self.sheet.get_width() // self.col
        self.h = self.sheet.get_height() // self.row
        self.color_key = color_key
        self.sprite_qty = sprite_qty
        self.sprites = []

    def get_sprite_at_pos(self, x, y):
        img = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        img.blit(self.sheet, (0, 0), pygame.Rect(x, y, self.w, self.h))
        img = pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor))
        if self.color_key is not None:
            img.set_colorkey(self.color_key)
        if self.is_flipped:
            return pygame.transform.flip(img, True, False)
        else:
            return img

    def get_images(self):
        c = 0
        images = []
        for i in range(self.row * self.col):
            c += 1
            if c > self.sprite_qty:
                break
            sprite = self.get_sprite_at_pos((i % self.col) * self.w, i % self.row * self.h)
            images.append(sprite)
        return images


bee_sprite_sheet = SpriteSheet(IMAGE_PATH, 14, 1, 14, scale_factor=8)
bee_sprite_sheet2 = SpriteSheet(IMAGE_PATH, 14, 1, 14, flipped=True, scale_factor=8)

pygame.display.set_icon(bee_sprite_sheet.get_images()[0])


def check_events(events):
    for e in events:
        if e.type == pygame.QUIT:
            sys.exit(0)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                sys.exit(0)


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


shell = win32com.client.Dispatch("WScript.Shell")
shell.SendKeys('%')


def main_game():
    global screen
    curr_sprite = 0
    bee_sprites_left = bee_sprite_sheet.get_images()
    bee_sprites_right = bee_sprite_sheet2.get_images()
    x = window_width // 2
    y = window_height // 2
    dx = 1
    dy = 1
    bee_horizontal_timer = time.time()
    bee_vertical_timer = time.time()
    size_x = 600
    size_y = 600
    no_frame = False
    alpha = 255
    hits = 0
    clicks = 0
    last_state = windll.user32.GetKeyState(0x01)
    while True:
        if hits >= 3:
            score_screen(hits, clicks)
            return
        if not no_frame:
            screen = pygame.display.set_mode((int(size_x), int(size_y)))
        else:
            screen = pygame.display.set_mode((int(size_x), int(size_y)), pygame.NOFRAME)
        Window.from_display_module().focus()
        size_x -= 1
        size_y -= 1
        flags, hcursor, (x1, y1) = win32gui.GetCursorInfo()
        if size_x < screen_width:
            size_x = screen_width
        if size_y < screen_height:
            size_y = screen_height
        if size_x == screen_width and size_y == screen_height:
            no_frame = True

        # bee movement i.e screen movement
        if time.time() - bee_vertical_timer > 0.25 * 10:
            bee_vertical_timer = time.time()
            dy = random.choice([-1, 0, 1])
        if time.time() - bee_horizontal_timer > 5:
            bee_horizontal_timer = time.time()
            dx = random.choice([-1, 0, 1])
        if x > window_width - screen_width // 2:
            bee_horizontal_timer = time.time()
            dx = -1
        if x < screen_width // 2:
            bee_horizontal_timer = time.time()
            dx = 1
        if y > window_height - screen_height // 2 + 50:
            bee_vertical_timer = time.time()
            dy = -1
        if y < screen_height // 2 - 75:
            bee_vertical_timer = time.time()
            dy = 1
        if distance((x1, y1), (x, y)) < 150:
            apply_alpha = True
            dx = -5 * math.cos(math.atan2(y1 - y, x1 - x))
            dy = -5 * math.sin(math.atan2(y1 - y, x1 - x))
        else:
            apply_alpha = False
        if no_frame:
            x += dx * 5
            y += dy * 5
            y += 5 * math.sin(time.time() * 5)
            pass

        if not apply_alpha:
            alpha += 1
            if alpha > 255:
                alpha = 255
        else:
            alpha -= 2

            if alpha < 0 + 50:
                alpha = 50

        bee_sprites = bee_sprites_left if dx < 0 else bee_sprites_right
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        curr_sprite += 1
        curr_sprite %= len(bee_sprites)
        events = pygame.event.get()
        if windll.user32.GetKeyState(0x01) not in [0, 1]:
            if windll.user32.GetKeyState(0x01) != last_state:
                last_state = windll.user32.GetKeyState(0x01)
                if no_frame:
                    clicks += 1

        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if no_frame:
                    mask = pygame.mask.from_surface(bee_sprites[curr_sprite])
                    if mask.get_rect().collidepoint(mx, my):
                        alpha = 100
                        hits += 1
        bee_sprites[curr_sprite].set_alpha(alpha)
        screen.fill((255, 0, 128))
        screen.blit(bee_sprites[curr_sprite], bee_sprites[curr_sprite].get_rect(center=screen.get_rect().center))
        if not no_frame:
            Text('Get Ready!', screen.get_rect().centerx, 50, 25, centered=True).draw()
        pygame.display.update()
        clock.tick(FPS)


def intro_screen():
    global screen
    x = window_width // 2
    y = window_height // 2
    size_x = 600
    size_y = 600
    screen = pygame.display.set_mode((size_x, size_y))
    bee_sprites = bee_sprite_sheet.get_images()
    curr_sprite = 0
    rect_h = 0
    while True:
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        events = pygame.event.get()
        check_events(events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    main_game()
                    screen = pygame.display.set_mode((size_x, size_y))
                    rect_h = 0
                if e.key == pygame.K_h:
                    help_screen()
                    rect_h = 0
                if e.key == pygame.K_c:
                    credits_screen()
                    rect_h = 0
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        curr_sprite += 1
        curr_sprite %= len(bee_sprites)
        screen.fill((255, 0, 128))
        screen.blit(bee_sprites[curr_sprite], bee_sprites[curr_sprite].get_rect(center=(screen.get_rect().centerx, 130)))
        pygame.draw.rect(screen, (255, 0, 127), (0, 260, screen.get_width(), rect_h))
        rect_h += 5
        if rect_h > screen.get_height() - 260:
            rect_h = screen.get_height() - 260
        Text('A Very Normal Game', screen.get_rect().centerx, 290, 30, centered=True).draw()
        Text('About A Bee', screen.get_rect().centerx, 330, 35, centered=True).draw()
        Text('Press Enter to Play', screen.get_rect().centerx, 400, 20, centered=True).draw()
        Text('Press Escape to Exit', screen.get_rect().centerx, 450, 20, centered=True).draw()
        Text('Press H for Help', screen.get_rect().centerx, 500, 20, centered=True).draw()
        Text('Press C for Credits', screen.get_rect().centerx, 550, 20, centered=True).draw()
        pygame.display.update()
        clock.tick(FPS)


def help_screen():
    global screen
    x = window_width // 2
    y = window_height // 2
    size_x = 600
    size_y = 600
    screen = pygame.display.set_mode((size_x, size_y))
    bee_sprites = bee_sprite_sheet.get_images()
    curr_sprite = 0
    rect_w = 0
    while True:
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        events = pygame.event.get()
        check_events(events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        curr_sprite += 1
        curr_sprite %= len(bee_sprites)
        screen.fill((255, 0, 128))
        screen.blit(bee_sprites[curr_sprite], bee_sprites[curr_sprite].get_rect(center=(screen.get_rect().centerx, 130)))
        pygame.draw.rect(screen, (255, 0, 127), (0, 260, rect_w, screen.get_height() - 260))
        rect_w += 10
        if rect_w > screen.get_width():
            rect_w = screen.get_width()
        Text('Click on the Bee', screen.get_rect().centerx, 300, 20, centered=True).draw()
        Text('using the left-mouse button', screen.get_rect().centerx, 350, 20, centered=True).draw()
        Text('Click on the Bee 3 times', screen.get_rect().centerx, 425, 20, centered=True).draw()
        Text('in order to win!', screen.get_rect().centerx, 475, 20, centered=True).draw()
        Text('Press Enter to go back', screen.get_rect().centerx, 550, 20, centered=True).draw()
        pygame.display.update()
        clock.tick(FPS)


def credits_screen():
    global screen
    x = window_width // 2
    y = window_height // 2
    size_x = 600
    size_y = 600
    screen = pygame.display.set_mode((size_x, size_y))
    bee_sprites = bee_sprite_sheet.get_images()
    curr_sprite = 0
    rect_w = 0
    while True:
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        events = pygame.event.get()
        check_events(events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        curr_sprite += 1
        curr_sprite %= len(bee_sprites)
        screen.fill((255, 0, 128))
        screen.blit(bee_sprites[curr_sprite], bee_sprites[curr_sprite].get_rect(center=(screen.get_rect().centerx, 130)))
        pygame.draw.rect(screen, (255, 0, 127), (screen.get_width() - rect_w, 260, rect_w, screen.get_height() - 260))
        rect_w += 10
        if rect_w > screen.get_width():
            rect_w = screen.get_width()
        Hyperlink('mrpoly', 475, 450, 20, centered=True, link='https://opengameart.org/content/menu-music').draw(events)
        Hyperlink('Ghast', 475, 400, 20, centered=True, link='https://ghastly.itch.io').draw(events)
        Hyperlink('Python', 390, 300, 20, centered=True, link='https://www.python.org').draw(events)
        Hyperlink('Pygame', 400, 350, 20, centered=True, link='https://www.pygame.org/docs/').draw(events)
        Hyperlink('Tank King', 400, 500, 20, centered=True, link='https://tank-king.itch.io').draw(events)
        Text('Language:       ', screen.get_rect().centerx, 300, 20, centered=True).draw()
        Text('Framework:       ', screen.get_rect().centerx, 350, 20, centered=True).draw()
        Text('Special Thanks to      ', screen.get_rect().centerx, 400, 20, centered=True).draw()
        Text('Background Music:       ', screen.get_rect().centerx, 450, 20, centered=True).draw()
        Text('A Game by:          ', screen.get_rect().centerx, 500, 20, centered=True).draw()
        Text('Press Enter to go back', screen.get_rect().centerx, 550, 15, centered=True).draw()
        pygame.display.update()
        clock.tick(FPS)


def score_screen(hits=0, clicks=0):
    global screen
    x = window_width // 2
    y = window_height // 2
    size_x = 600
    size_y = 600
    screen = pygame.display.set_mode((size_x, size_y))
    bee_sprites = bee_sprite_sheet.get_images()
    curr_sprite = 0
    rect_h = 0
    if clicks == 0:
        clicks = 1
    while True:
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        events = pygame.event.get()
        check_events(events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return
        Window.from_display_module().position = (x - size_x // 2, y - size_y // 2)
        curr_sprite += 1
        curr_sprite %= len(bee_sprites)
        screen.fill((255, 0, 128))
        screen.blit(bee_sprites[curr_sprite], bee_sprites[curr_sprite].get_rect(center=(screen.get_rect().centerx, 130)))
        pygame.draw.rect(screen, (255, 0, 127), (0, screen.get_height() - rect_h, screen.get_width(), rect_h))
        rect_h += 5
        if rect_h > screen.get_height() - 260:
            rect_h = screen.get_height() - 260
        Text('STATS', screen.get_rect().centerx, 300, 25, centered=True).draw()
        Text('Hits     : ' + str(hits), 50, 340, 20).draw()
        Text('Clicks   : ' + str(clicks), 50, 380, 20).draw()
        accuracy = 100 * hits / clicks
        # to ensure that the accuracy is shown in decimals when less than 1 and decimal is rounded off to 2 places
        accuracy = int(accuracy) if int(accuracy) > 0 else int(accuracy * 100) / 100
        Text('Accuracy : ' + str(accuracy) + '%', 50, 420, 20).draw()
        pygame.display.update()
        clock.tick(FPS)


pygame.mixer.music.load(SOUND_PATH)
pygame.mixer.music.play(-1)
intro_screen()
