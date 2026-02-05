import random
import sys

import pygame

from scripts.dualgridtilemap import DualGridTilemap
from scripts.tilemap import Tilemap
from scripts.utils import *
from scripts.player import Player


class Game:
    def __init__(self):
        pygame.init()

        self.gravity = 0.05

        self.tile_size = 16
        self.setup_screen()

        self.clock = pygame.time.Clock()

        self.assets = {
            "stone": Tileset(load_image("tiles/stone.png"), self.tile_size),
            "brick":Tileset(load_image("tiles/brick.png"), self.tile_size),
            "ore" : Tileset(load_image("tiles/ores.png"), self.tile_size),
            "hazard":Tileset(load_image("tiles/hazard.png"), self.tile_size),
            "player/swing" : Animation("player/swing", 1, loop=False)
        }
        self.sounds = {
            # "jump" : load_sfx("jump.wav")
        }

        self.input = [False, False, False, False]
        self.holding_attack = False
        self.screen_shake = 0

        self.fps = 0
        self.running = False

    def start_game(self):
        self.running = True
        self.game_state = "mainmenu"

        self.tilemap = Tilemap(self, self.tile_size)
        self.dualgrids = [
            DualGridTilemap(self.tilemap, ["stone", "ore"]),
            DualGridTilemap(self.tilemap, ["brick"])
        ]

        self.player = Player(self, [2 * self.tile_size, -1 * self.tile_size])

        self.reset()

    def attack_tile(self, tile_pos, dmg=-1):
        destroyed, dmg = self.tilemap.damage_tile([tile_pos[0], tile_pos[1]], dmg)
        # second shot makes more shake, final shot shakes even more
        if dmg != 0:
            self.set_shake(10 + 5 * (dmg > 1) + 5 * (destroyed == True and dmg > 1))
        if destroyed:
            for dualgrid in self.dualgrids:
                dualgrid.tile_changed(tile_pos[0], tile_pos[1])
        return destroyed, dmg

    def reset(self):
        self.cam_pos = [0, 0]
        self.cutscene = None

        self.map_bottom = 0

        self.load_map("test", clear=True, generate=False)

        self.sparks = []
        self.entities = []

        self.player.reset()

    def load_map(self, path, ores=True, clear=False, generate=True):
        self.tilemap.load_map(path, [0, self.map_bottom], ores, clear, generate)

        for dualgrid in self.dualgrids:
            dualgrid.autotile_all()

        self.map_bottom += 7

        self.tilemap.clear_above(self.map_bottom-21)

    def run(self):
        self.start_game()
        while self.running:
            self.screen.fill((0, 0, 0))
            self.take_input()

            if self.game_state == "mainmenu":
                self.screen.fill((255, 0, 0))
            elif self.game_state == "game":
                self.game_frame()
            elif self.game_state == "win":
                pass

            self.update_cutscene()

            self.display.blit(pygame.transform.scale(self.screen, self.display_size))
            pygame.display.update()
            self.fps = self.clock.tick(60)

    def game_frame(self):
        # how does this work????
        target_y = (self.player.pos[1] + self.player.size[1] - self.screen_size[1] // 4)
        target_y = target_y // self.tile_size * self.tile_size
        if (self.player.pos[1] + self.player.size[1]-self.cam_pos[1])>self.tile_size*4:

            self.cam_pos[1] += (target_y - self.cam_pos[1])*0.03

        if self.player.pos[1] > (self.map_bottom-7)*self.tile_size:
            self.load_map("test")

        # Camera offset
        if self.screen_shake > 0:
            self.screen_shake -= 1
        offset = [int(self.cam_pos[0] + random.random() * self.screen_shake//5), int(self.cam_pos[1] + random.random() * self.screen_shake//5)]

        for entity in self.entities:
            entity.update(1)
            entity.render(self.screen, offset)

        if self.holding_attack:
            self.player.swing()

        self.player.update(self.input)
        self.player.pos[0] = max(0, min(self.player.pos[0], 8 * self.tile_size - self.player.size[0]))
        self.player.pos[1] = max(self.player.pos[1], int(self.cam_pos[1]))
        self.player.render(self.screen, offset)

        # Tilemap
        for dualgrid in self.dualgrids:
            dualgrid.render(self.screen, offset)
        self.tilemap.render(self.screen, offset)

        # Sparks
        for spark in self.sparks.copy():
            done = spark.update()
            if done:
                self.sparks.remove(spark)
            else:
                spark.render(self.screen, offset)

    def take_input(self):
        left = pygame.K_a
        right = pygame.K_d
        up = pygame.K_w
        down = pygame.K_s
        attack = [pygame.K_k]
        jump = [pygame.K_j]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in jump and self.game_state == "game":
                    self.player.jumping = True
                    self.player.jump()
                if event.key in attack:
                    self.holding_attack = True

                if event.key == pygame.K_r:
                    self.reset()

                if event.key == up:
                    self.input[0] = True
                if event.key == right:
                    self.input[1] = True
                if event.key == down:
                    self.input[2] = True
                if event.key == left:
                    self.input[3] = True

                if self.game_state == "mainmenu":
                    self.game_state = "game"
            elif event.type == pygame.KEYUP:
                if event.key in jump:
                    self.player.jumping = False
                if event.key in attack:
                    self.holding_attack = False

                if event.key == up:
                    self.input[0] = False
                if event.key == right:
                    self.input[1] = False
                if event.key == down:
                    self.input[2] = False
                if event.key == left:
                    self.input[3] = False

    def update_cutscene(self):
        if self.cutscene:
            done = self.cutscene.update()
            if done:
                self.cutscene = None

    def set_shake(self, shake):
        if shake > self.screen_shake:
            self.screen_shake = shake

    def setup_screen(self):
        self.screen_size = [self.tile_size * 8, self.tile_size * 8]
        self.screen = pygame.surface.Surface(self.screen_size)

        self.enlargement = 5
        self.display_size = [self.screen_size[0] * self.enlargement, self.screen_size[1] * self.enlargement]
        self.display = pygame.display.set_mode(self.display_size, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED,
                                               vsync=1)
        pygame.display.set_caption('Miner')

game = Game()
game.run()
