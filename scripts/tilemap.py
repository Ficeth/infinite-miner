import pygame
from math import floor, ceil
import json
import random
import noise

PHYSICS_TILES = ['stone', 'ore', 'brick', 'hazard']

TYPE_HEALTH = {
    "stone":1,
    "ore":3,
    "brick":3,
    "hazard":1,
}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.screen_size = game.screen_size

        self.tile_size = tile_size

        self.tiles = {
            # idx : [ type , num, pos, health]
        }

    def save_map(self, file_path):
        file = open(f"maps/{file_path}.json", 'w')
        json.dump(self.tiles, file)

    def clear_above(self, tile_y):
        deletable = []
        for idx in self.tiles.keys():
            tile = self.tiles[idx]
            if tile[2][1] < tile_y:
                deletable.append(idx)

        for idx in deletable:
            del self.tiles[idx]

    def damage_tile(self, tile_pos, dmg = -1):
        total_dmg = 0
        idx = "{" + str(tile_pos[0]) + ":" + str(tile_pos[1]) + "}"
        if not idx in self.tiles:
            return False, total_dmg

        tile = self.tiles[idx]
        if tile[3] + dmg <= 0:
            total_dmg = TYPE_HEALTH[tile[0]]
            del self.tiles[idx]
            return True, total_dmg
        else:
            total_dmg = TYPE_HEALTH[tile[0]] - tile[3] + 1
            self.tiles[idx] = [tile[0], tile[1], tile[2], tile[3] + dmg]
            return False, total_dmg

    def load_map(self, file_path, offset=[0, 0], ores=True, clear = False, generate=False):
        if clear:
            self.tiles = {}

        if generate:
            self.procedural_map(offset, ores)
            return

        try:
            self.load_map_file(file_path, offset, ores)
        except FileNotFoundError:
            pass


    def set_tile(self, tile_type, tile_pos):
        idx = "{" + str(tile_pos[0]) + ":" + str(tile_pos[1]) + "}"
        if tile_type == -1:
            if idx in self.tiles:
                del self.tiles[idx]
        else:
            self.tiles[idx] = [tile_type, 0, [tile_pos[0], tile_pos[1]], TYPE_HEALTH[tile_type]]


    def check_collision(self, rect):
        # only check the tiles around the rect, determined by size
        # ie if rect is 1x1 tiles, check a 3x3 area
        # but if rect is 2x1, check 4x3 area
        x_range = ceil(rect.width/self.tile_size) + 2
        y_range = ceil(rect.height/self.tile_size) + 2

        for x in range(x_range):
            for y in range(y_range):
                offset = [x - floor(x_range/2), y - floor(y_range/2)]
                tile_x = (int(rect.x) + rect.width // 2) // self.tile_size + offset[0]
                tile_y = (int(rect.y) + rect.height // 2) // self.tile_size + offset[1]

                if self.is_physics_tile([tile_x * self.tile_size, tile_y * self.tile_size]):

                    r = pygame.Rect(tile_x * self.tile_size, tile_y * self.tile_size, self.tile_size, self.tile_size)
                    if rect.colliderect(r):
                        return r
        return None

    def is_physics_tile(self, pos):
        tile = self.get_tile(pos)
        if tile:
            if tile[0] in PHYSICS_TILES:
                return tile[0]
        return False


    def get_tile(self, pos):
        tile_x = round(pos[0] // self.tile_size)
        tile_y = round(pos[1] // self.tile_size)
        idx = "{" + str(tile_x) + ":" + str(tile_y) + "}"
        tile = False
        if idx in self.tiles:
            tile = self.tiles[idx]

        return tile

    def load_map_file(self, file_path, offset, ores):
        with open(f"maps/{file_path}.json") as file:
            new_tiles = json.load(file)
            for tile in new_tiles.values():
                new_pos = [tile[2][0] + offset[0], tile[2][1] + offset[1]]
                idx = "{" + str(new_pos[0]) + ":" + str(new_pos[1]) + "}"
                type = tile[0]
                num = tile[1]
                if tile[0] == "stone" and ores:
                    rand = random.randint(1, 100)
                    if rand <= 1:
                        # diamond
                        type = "ore"
                        num = 1
                    elif rand <= 3:
                        # mini diamond
                        type = "ore"
                        num = 2
                    elif rand <= 8:
                        # quartz
                        type = "ore"
                        num = 0

                self.tiles[idx] = [type, num, [new_pos[0], new_pos[1]], TYPE_HEALTH[type]]

    def procedural_map(self, offset, ores):
        for not_y in range(8):
            for x in range(8):
                y = not_y + 1

                f = x  # 0 : 7
                f = (f + 0) % 8  # 0 : 7
                f += 1
                f -= 4.5  # -3.5 : 3.5
                f = abs(f)  # 3.5 : 0 : 3.5
                f /= 3.5  # 1 : 0 : 1
                fill_incentive = 0.0 + 0.1 * f

                noise_val = noise.snoise3(x * 0.1, y * 0.1, random.randint(0, 1024)) + fill_incentive
                new_pos = [x + offset[0], y + offset[1]]
                idx = "{" + str(new_pos[0]) + ":" + str(new_pos[1]) + "}"

                type = "stone"
                num = 0
                if ores:
                    rand = random.randint(1, 100)
                    if rand <= 3:
                        # diamond
                        type = "ore"
                        num = 1
                    elif rand <= 5:
                        # mini diamond
                        type = "ore"
                        num = 2
                    elif rand <= 7:
                        # quartz
                        type = "ore"
                        num = 0
                    elif rand <= 75:
                        pass
                    else:
                        type = "brick"

                if noise_val < 0:
                    continue



                self.tiles[idx] = [type, num, [new_pos[0], new_pos[1]], TYPE_HEALTH[type]]

    def update(self):
        pass

    def render(self, screen, offset=[0, 0]):
        x_range = self.screen_size[0] // self.tile_size + 2
        y_range = self.screen_size[1] // self.tile_size + 2

        for local_tile_y in range(y_range):
            for local_tile_x in range(x_range):
                global_tile_x = offset[0] // self.tile_size + local_tile_x
                global_tile_y = offset[1] // self.tile_size + local_tile_y

                idx = "{" + str(global_tile_x) + ":" + str(global_tile_y) + "}"
                if idx in self.tiles:
                    tile = self.tiles[idx]

                    local_x = local_tile_x * self.tile_size - offset[0] % self.tile_size
                    local_y = local_tile_y * self.tile_size - offset[1] % self.tile_size

                    tile_img = None
                    if tile[0] == "ore":
                        tile_img = self.game.assets["ore"].get_tile(tile[1])
                    elif tile[0] == "hazard":
                        tile_img = self.game.assets["hazard"].get_tile(tile[1])

                    if tile_img:
                        screen.blit(tile_img, [local_x, local_y])
                    # White collision box
                    #pygame.draw.rect(screen, (255, 255, 255), [local_x, local_y, self.tile_size+1, self.tile_size+1], 1)