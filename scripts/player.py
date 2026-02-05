import random

from scripts.entity import Entity
from scripts.spark import Spark

from math import pi, sin

class Player(Entity):
    def __init__(self, game, pos):
        super().__init__(game, pos, [game.tile_size-10, game.tile_size-6], "player")

        self.input = [False, False, False, False]
        self.jumping = False
        self.was_jumping = False
        self.wall_time = 4
        self.wall_dir = 0
        self.swinging = False

        # Constants
        self.max_fall = 2

        # Upgrades
        self.dmg = -1

        self.anim_offset = [5, 6]
        self.set_anim("swing")

    def jump(self):
        if not self.can_move:
            return

        if self.air < 8:
            self.air = 8
            self.was_jumping = True
            self.stored_vel[1] = -2
        elif self.wall_time < 4:
            self.stored_vel[1] = -1.5
            self.stored_vel[0] = -3 * self.wall_dir

    def swing(self):
        if not self.can_move:
            return

        if self.anim_name == "swing" and not self.anim.done:
            return

        self.set_anim("swing", reset=True)
        self.swinging = True

    def attack_block(self):
        mine_dir = [(self.input[1] - self.input[3]), (self.input[2] - self.input[0])]
        if mine_dir[1] != 0:
            mine_dir[0] = 0
        elif mine_dir[0] == 0:
            mine_dir[0] = self.last_dir

        tile_x = int((self.pos[0] + self.size[0] // 2) // self.game.tile_size)
        tile_y = int((self.pos[1] + self.size[1] // 2) // self.game.tile_size)

        destroyed, dmg = self.game.attack_tile([tile_x + mine_dir[0], tile_y + mine_dir[1]], self.dmg)
        angle = 0
        if mine_dir[1] != 0: angle += (pi / 2) * mine_dir[1]
        if mine_dir[0] == -1: angle = pi
        pos = [self.pos[0] + self.size[0]//2, self.pos[1] + self.size[1]//2]

        for i in range(50):
            rand = i/50*1.25 - 0.625
            new_spark = Spark([pos[0], pos[1]], angle + rand, 2.0  - 0.3*abs(sin(rand)))
            self.game.sparks.append(new_spark)

        if destroyed:
            pass

    def update(self, input):
        super().update(input[1] - input[3])

        if self.jumping and self.stored_vel[1] < -1:
            self.gravity = self.game.gravity
        else:
            if self.was_jumping and not self.jumping:
                self.stored_vel[1] = max(self.stored_vel[1], -1)
            self.was_jumping = False
            if self.stored_vel[1] < 0.1:
                self.gravity = self.game.gravity * 1
            else:
                self.gravity = self.game.gravity * 2

        self.wall_time += 1
        if self.collision[1] or self.collision[3]:
            self.wall_time = 0
            if self.collision[1] and input[1] - input[3] > 0:
                self.wall_dir = 1
            elif self.collision[3] and input[1] - input[3] < 0:
                self.wall_dir = -1
            if self.vel[1] > 0:
                self.gravity = min(self.gravity, self.game.gravity / 4)
            self.stored_vel[1] = min(self.stored_vel[1], self.max_fall / 4)
        else:
            self.stored_vel[1] = min(self.stored_vel[1], self.max_fall)

        self.input = input

        if self.swinging and self.anim_name == "swing" and self.anim.curr_frame >= 1:
            self.swinging = False
            self.attack_block()

    def render(self, screen, offset):
        super().render(screen, offset)