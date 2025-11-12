# arrow.py
from pico2d import load_image

import game_framework
import game_world

PIXEL_PER_METER = (10.0 / 0.3)
ARROW_SPEED_KMPH = 10.0
ARROW_SPEED_MPM = (ARROW_SPEED_KMPH * 1000.0 / 60.0)
ARROW_SPEED_MPS = (ARROW_SPEED_MPM / 60.0)
ARROW_SPEED_PPS = (ARROW_SPEED_MPS * PIXEL_PER_METER)

class Arrow:
    image = None

    def __init__(self, x = 0, y = 0, face_dir = 1):
        if Arrow.image == None:
            Arrow.image = load_image('samurai_Archer/Arrow.png')
        self.x, self.y = x, y
        self.face_dir = face_dir

    def draw(self):
        if self.face_dir == 1:
            self.image.clip_draw(0, 0, 50, 50, self.x, self.y)
        else:
            self.image.clip_composite_draw(0, 0, 50, 50, 0, 'h', self.x, self.y, 50, 50)

    def update(self):
        self.x += self.face_dir * ARROW_SPEED_PPS * game_framework.frame_time

    def get_bb(self):
        return self.x - 25, self.y - 25, self.x + 25, self.y + 25

    def handle_collision(self, group, other):
        if group == 'samurai_Archer:arrow':
            game_world.remove_object(self)