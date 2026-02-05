import pygame
import json

AUTOTIlE_GRID = {
    "[0, 0, 0, 0]":-1,
    "[0, 0, 0, 1]": 0,
    "[0, 0, 1, 0]": 12,
    "[0, 0, 1, 1]": 3,
    "[0, 1, 0, 0]": 8,
    "[0, 1, 0, 1]": 13,
    "[0, 1, 1, 0]": 1,
    "[0, 1, 1, 1]": 5,
    "[1, 0, 0, 0]": 14,
    "[1, 0, 0, 1]": 11,
    "[1, 0, 1, 0]": 4,
    "[1, 0, 1, 1]": 2,
    "[1, 1, 0, 0]": 9,
    "[1, 1, 0, 1]": 7,
    "[1, 1, 1, 0]": 10,
    "[1, 1, 1, 1]": 6,
}

class DualGridTilemap:
    # offset by negative half a tile

    def __init__(self, tilemap, mat_list=["stone", "ore"]):
        self.game = tilemap.game
        self.screen_size = tilemap.screen_size

        self.mat_list = mat_list

        self.tilemap = tilemap

        self.tile_size = tilemap.tile_size

        self.tiles = {
            # idx : [ type , num, pos ]
        }

    def save_map(self, file_path):

        file = open(f"maps/{file_path}_{self.mat_list[0]}.json", 'w')
        json.dump(self.tiles, file)

    def load_map(self, file_path, offset=[0, 0], clear=False):
        if clear:
            self.tiles = {}

        try:
            with open(f"maps/{file_path}_{self.mat_list[0]}.json") as file:
                new_tiles = json.load(file)
                for tile in new_tiles.values():
                    new_pos = [tile[2][0] + offset[0], tile[2][1] + offset[1]]
                    idx = "{" + str(new_pos[0]) + ":" + str(new_pos[1]) + "}"
                    self.tiles[idx] = [tile[0], tile[1], [new_pos[0], new_pos[1]]]
        except FileNotFoundError:
            pass

    def clear_above(self, tile_y):
        deletable = []
        for idx in self.tiles.keys():
            tile = self.tiles[idx]
            if tile[2][1] < tile_y:
                deletable.append(idx)

        for idx in deletable:
            del self.tiles[idx]

    def autotile_all(self):
        for tile in self.tilemap.tiles.values():
            if tile[0] in self.mat_list:
                self.tile_changed(tile[2][0], tile[2][1])

        deletable = []
        for idx in self.tiles.keys():
            tile = self.tiles[idx]
            exists = False
            for tile_pos in [[tile[2][0], tile[2][1]], [tile[2][0] -1, tile[2][1]], [tile[2][0] - 1, tile[2][1] - 1], [tile[2][0], tile[2][1] - 1]]:
                new_idx = "{" + str(tile_pos[0]) + ":" + str(tile_pos[1]) + "}"
                if new_idx in self.tilemap.tiles:
                    if self.tilemap.tiles[new_idx][0] in self.mat_list:
                        exists = True
            if not exists:
                deletable.append(idx)

        for idx in deletable:
            del self.tiles[idx]
        pass

    def tile_changed(self, tile_x, tile_y):
        # iterate through the 4 dual tiles around collision tile changed
        for tile_pos in [[tile_x, tile_y], [tile_x + 1, tile_y], [tile_x + 1, tile_y + 1], [tile_x, tile_y + 1]]:
            idx = "{" + str(tile_pos[0]) + ":" + str(tile_pos[1]) + "}"
            self.tiles[idx] = [self.mat_list[0], 0, [tile_pos[0], tile_pos[1]]]

            # iterate through the 4 collision tiles around each dual tile, then autotile the dual tile
            side_tiles = [0, 0, 0, 0]
            tile_check = 0
            for tile_offset in [[-1, -1], [0, -1], [0, 0], [-1, 0]]:
                side_x = tile_pos[0] + tile_offset[0]
                side_y = tile_pos[1] + tile_offset[1]
                side_idx = "{" + str(side_x) + ":" + str(side_y) + "}"
                if side_idx in self.tilemap.tiles:
                    if self.tilemap.tiles[side_idx][0] in self.mat_list:
                        side_tiles[tile_check] = 1
                tile_check += 1

            side_tiles = "[" + str(side_tiles[0]) + ", " + str(side_tiles[1]) + ", " + str(side_tiles[2]) + ", " + str(
                side_tiles[3]) + "]"

            autotile_idx = -1
            if side_tiles in AUTOTIlE_GRID:
                autotile_idx = AUTOTIlE_GRID[side_tiles]

            if autotile_idx == -1:
                del self.tiles[idx]
            else:
                self.tiles[idx] = [self.mat_list[0], autotile_idx, [tile_pos[0], tile_pos[1]]]

    def render(self, screen, offset=[0, 0]):
        offset = [offset[0] + self.tile_size//2, offset[1] + self.tile_size//2]

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
                    if tile[0] == "stone":
                        tile_img = self.game.assets["stone"].get_tile(tile[1])
                    elif tile[0] == "brick":
                        tile_img =self.game.assets["brick"].get_tile(tile[1])

                    # Red debug box
                    #pygame.draw.rect(screen, (255, 0, 0), [local_x, local_y, self.tile_size, self.tile_size], 1)

                    if tile_img:
                        screen.blit(tile_img, [local_x, local_y])