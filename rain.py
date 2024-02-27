import pyxel
import random
from enum import Enum, IntEnum, auto

class Scene(Enum):
    START = auto()
    PLAY = auto()
    END = auto()

class Col(IntEnum):
    PLAYER = 12
    ENEMY = 8

W = H = 256

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

class Rect:
    def __init__(self, x, y, w, h, col):
        self.pos = Vector2(x, y)
        self.w = w
        self.h = h
        self.col = col

    def draw(self):
        pyxel.rect(self.pos.x, self.pos.y, self.w, self.h, self.col)

LIFE = 3
PLAYER_W = 64
PLAYER_H = 16
PLAYER_VEL = 16

class Player(Rect):
    def __init__(self):
        super().__init__(x=W//2-PLAYER_W//2, y=H*3//4, \
                         w=PLAYER_W, h=PLAYER_H, col=Col.PLAYER)
        self.point = 0
        self.life = LIFE

    def update(self):
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if self.pos.x + self.w / 2 < pyxel.mouse_x:
                self.pos += Vector2(PLAYER_VEL, 0)
            if self.pos.x + self.w / 2 > pyxel.mouse_x:
                self.pos += Vector2(-PLAYER_VEL, 0)

        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x + self.w > W:
            self.pos.x = W - self.w

    def coll(self, rain):
        return self.pos.x < rain.pos.x < self.pos.x + self.w \
           and self.pos.y < rain.pos.y < self.pos.y + self.h

RAIN_W = 2
RAIN_H = 8
RAIN_VEL = 8

class Rain(Rect):
    def __init__(self, x, y, col):
        super().__init__(x, y, RAIN_W, RAIN_H, col)
        self.vel = Vector2(0, RAIN_VEL)
        
    def update(self):
        self.pos += self.vel

    def is_out(self):
        return self.pos.y > H

INTERVAL_MAX = 10
INTERVAL_MIN = 4
THRESHOLD_MAX = 0.8
THRESHOLD_MIN = 0.4
MAX_DIFFICULTY_POINT = 200

def ctext(x, y, s, col):
    dx = len(s) * 2
    pyxel.text(x - dx, y, s, col)

class App:
    def __init__(self):
        pyxel.init(W, H, title="Rain")
        self.player = Player()
        self.rains = []
        self.t = 0
        self.scene = Scene.START
        self.prev_pressed = False
        pyxel.mouse(True)
        pyxel.load("rain.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        self.t += 1

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if not self.prev_pressed and self.scene == Scene.START:
                self.scene = Scene.PLAY
            if not self.prev_pressed and self.scene == Scene.END:
                self.player = Player()
                self.rains = []
                self.scene = Scene.START
            self.prev_pressed = True
        else:
            self.prev_pressed = False
        
        if self.scene != Scene.PLAY:
            return

        interval = max(INTERVAL_MIN, INTERVAL_MAX - (INTERVAL_MAX - INTERVAL_MIN) * self.player.point / MAX_DIFFICULTY_POINT)
        threshold = max(THRESHOLD_MIN, THRESHOLD_MAX - (THRESHOLD_MAX - THRESHOLD_MIN) * self.player.point / MAX_DIFFICULTY_POINT)
        if self.t % int(interval) == 0:
            random_ = random.random()
            if random_ < threshold:
                self.rains.append(Rain(random.random() * W, 0, Col.PLAYER))
            else:
                self.rains.append(Rain(random.random() * W, 0, Col.ENEMY))

        self.player.update()
        for rain in self.rains:
            rain.update()
            if rain.is_out():
                self.rains.remove(rain)
            elif self.player.coll(rain):
                if rain.col == Col.PLAYER:
                    self.player.point += 1
                    pyxel.play(1, 0, loop=False)
                elif rain.col == Col.ENEMY:
                    self.player.life -= 1
                    pyxel.play(1, 1, loop=False)
                    if self.player.life <= 0:
                        self.scene = Scene.END
                self.rains.remove(rain)

    def draw(self):
        pyxel.cls(0)

        self.player.draw()
        for rain in self.rains:
            rain.draw()

        if self.scene == Scene.START:
            ctext(W // 2, H // 2, "START", Col.PLAYER)
        if self.scene == Scene.PLAY:
            ctext(W // 2, H // 2, '[]' * self.player.life, Col.ENEMY)
            ctext(W // 2, H // 2 + 8, str(self.player.point), Col.PLAYER)
        if self.scene == Scene.END:
            ctext(W // 2, H // 2, "END", Col.ENEMY)
            ctext(W // 2, H // 2 + 8, str(self.player.point), Col.PLAYER)

App()
