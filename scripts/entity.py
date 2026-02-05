import pygame

class Entity:
    def __init__(self, game, pos, size, name="entity"):
        self.game = game
        self.spawn = [pos[0], pos[1]]
        self.pos = [pos[0], pos[1]]
        self.size = [size[0], size[1]]

        self.name = name
        self.anim = None
        self.anim_name = None
        self.anim_offset = [3, 3]

        self.stored_vel = [0, 0]
        self.vel = [0, 0]
        self.last_dir = 1
        self.gravity = self.game.gravity

        self.air = 0
        self.collision = [False, False, False, False]

        self.max_health = 3
        self.health = self.max_health
        self.speed = 1

        self.can_move = True

        self.reset()

    def reset(self):
        self.pos = [self.spawn[0], self.spawn[1]]

        self.stored_vel = [0, 0]
        self.vel = [0, 0]
        self.last_dir = 1

        self.health = self.max_health

    def get_rect(self):
        return pygame.Rect([*self.pos, *self.size])

    def set_anim(self, anim_name, reset=False):
        if anim_name != self.anim_name or reset:
            self.anim_name = anim_name
            self.anim = self.game.assets[f"{self.name}/{self.anim_name}"]
            self.anim.reset()

    def update(self, movement=0):
        self.collision = [False, False, False, False]

        self.air += 1
        self.stored_vel[1] += self.gravity

        self.vel = [self.stored_vel[0], self.stored_vel[1]]

        speed_in_move_dir = False
        if self.stored_vel[0] != 0:
            speed_in_move_dir = (movement == ( self.stored_vel[0]/abs(self.stored_vel[0]) ) )
        speed_faster_than_move = (abs(self.stored_vel[0] >= self.speed))
        # if you can move, and your velocity is not faster than your move speed, then add move speed
        # this is because when wall jumping, move speed + wall jump is too fast
        if self.can_move and not (speed_in_move_dir and speed_faster_than_move):
            self.vel[0] += movement * self.speed

        self.pos[0] += self.vel[0]
        col_rect = self.game.tilemap.check_collision(self.get_rect())
        if col_rect and self.vel[0] != 0:
            vel_dir = self.vel[0] / abs(self.vel[0])
            if vel_dir > 0:
                self.pos[0] = col_rect.x - self.size[0]
                self.collision[1] = True
            else:
                self.pos[0] = col_rect.x + col_rect.width
                self.collision[3] = True
            self.stored_vel[0] = 0

        self.pos[1] += self.vel[1]
        col_rect = self.game.tilemap.check_collision(self.get_rect())
        if col_rect and self.vel[1] != 0:
            vel_dir = self.vel[1] / abs(self.vel[1])
            if vel_dir > 0:
                self.air = 0
                self.pos[1] = col_rect.y - self.size[1]
                self.collision[2] = True
            else:
                self.pos[1] = col_rect.y + col_rect.height
                self.collision[0] = True
            self.stored_vel[1] = 0

        if self.air < 4:
            self.stored_vel[0] *= 0.7
        else:
            self.stored_vel[0] *= 0.8

        if movement != 0:
            self.last_dir = movement

        if self.can_move:
            self.anim.update()

    def render(self, screen, offset):
        if self.anim:
            img = self.anim.get_img()
            img = pygame.transform.flip(img, self.last_dir==-1, False)
            screen.blit(img, [int(self.pos[0]) - offset[0] - self.anim_offset[0], int(self.pos[1]) - offset[1] - self.anim_offset[1]])
        else:
            pygame.draw.rect(screen, (0, 0, 255),
                             [int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1]), *self.size])