import pygame
from math import sin, cos, pi

class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = pos
        self.angle = angle
        self.speed = speed



        self.scale = 4

        self.pos[0] += cos(self.angle) * self.speed * self.scale * 1.5
        self.pos[1] += sin(self.angle) * self.speed * self.scale * 1.5


    def update(self):
        self.pos = [self.pos[0] + cos(self.angle) * self.speed * 0.5, self.pos[1] + sin(self.angle) * self.speed * 0.5]

        self.speed -= 0.2
        if self.speed <= 0:
            return True

        return False

    def render(self, screen, offset):
        pos = [self.pos[0] - offset[0], self.pos[1] - offset[1]]

        points = [
            [(pos[0] + cos(self.angle) * self.speed * self.scale * 0.0), (pos[1] + sin(self.angle) * self.speed * self.scale * 0.0)],
            [(pos[0] + cos(self.angle + pi/2) * self.speed * self.scale * 0.3), (pos[1] + sin(self.angle + pi/2) * self.speed * self.scale * 0.3)],
            [(pos[0] - cos(self.angle) * self.speed * self.scale * 0.3), (pos[1] - sin(self.angle) * self.speed * self.scale * 0.3)],
            [(pos[0] + cos(self.angle - pi/2) * self.speed * self.scale * 0.3), (pos[1] + sin(self.angle - pi/2) * self.speed * self.scale * 0.3)],
        ]

        pygame.draw.polygon(screen, (255, 255, 255), points)