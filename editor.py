import sys
import pygame
import random

from scripts.utils import *
from scripts.tilemap import Tilemap
from scripts.dualgridtilemap import DualGridTilemap


class Game:
    def __init__(self):
        self.curr_type = "stone"

        pygame.init()

        self.tile_size = 16
        self.screen_size = [self.tile_size * 8, self.tile_size * 8]
        self.screen = pygame.surface.Surface(self.screen_size)

        self.enlargement = 5
        self.display_size = [self.screen_size[0] * self.enlargement, self.screen_size[1] * self.enlargement]
        self.display = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption('Editor')

        self.clock = pygame.time.Clock()

        self.assets = {
            "stone": Tileset(load_image("tiles/stone.png"), self.tile_size),
            "brick": Tileset(load_image("tiles/brick.png"), self.tile_size),
            "ore": Tileset(load_image("tiles/ores.png"), self.tile_size),
            # "player" : load_image("player.png")
        }
        self.sounds = {
            # "jump" : load_sfx("jump.wav")
        }

        self.mouse_down = False
        self.shifting = False

        self.screen_shake = 0

        self.fps = 0
        self.running = False

    def start_game(self):
        self.running = True
        self.game_state = "mainmenu"

        self.cam_pos = [0, 0]

        self.cutscene = None
        self.tilemap = Tilemap(self, self.tile_size)
        self.tilemap.load_map("test")
        self.dualgrids = [
            DualGridTilemap(self.tilemap, ["stone", "ore"]),
            DualGridTilemap(self.tilemap, ["brick"])
        ]
        for dualgrid in self.dualgrids:
            dualgrid.load_map("test")
        self.sparks = []
        self.entities = []

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
        mpos = pygame.mouse.get_pos()
        mpos = [mpos[0] // self.enlargement, mpos[1] // self.enlargement]

        # Camera offset
        if self.screen_shake > 0:
            self.screen_shake -= 1
        offset = [int(self.cam_pos[0] + random.random() * self.screen_shake), int(self.cam_pos[1] + random.random() * self.screen_shake)]

        if self.mouse_down:
            tile_type = self.curr_type
            if self.shifting:
                tile_type = -1

            tile_pos = [mpos[0]//self.tile_size, mpos[1]//self.tile_size]
            self.tilemap.set_tile(tile_type, tile_pos)
            for dualgrid in self.dualgrids:
                dualgrid.tile_changed(*tile_pos)

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LSHIFT:
                    self.shifting = True
                if event.key == pygame.K_o:
                    self.tilemap.save_map("test")
                    for dualgrid in self.dualgrids:
                        dualgrid.save_map("test")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    self.shifting = False

                if self.game_state == "mainmenu":
                    self.game_state = "game"

    def update_cutscene(self):
        if self.cutscene:
            done = self.cutscene.update()
            if done:
                self.cutscene = None

    def set_shake(self, shake):
        if shake > self.screen_shake:
            self.screen_shake = shake

game = Game()
game.run()
