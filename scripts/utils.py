import pygame

def load_image(path):
    img = pygame.image.load("assets/" + path).convert_alpha()
    return img

def load_sfx(path, vol=1.0):
    sound = pygame.mixer.Sound("sounds/" + path)
    sound.set_volume(vol)
    return sound

def play_music(path, loops=-1, vol=1.0):
    pygame.mixer.music.load("sounds/" + path)
    pygame.mixer.music.set_volume(vol)
    pygame.mixer.music.play(loops)

class Animation:
    def __init__(self, file_path, anim_speed, loop=True):
        self.anim_speed = anim_speed
        self.imgs = []
        self.anim_length = 0
        for i in range(50):
            num = str(i)
            if i < 10:
                num = f"0{num}"
            path = f"{file_path}/{num}.png"
            try:
                img = load_image(path)
                self.imgs.append(img)
            except FileNotFoundError:
                self.anim_length = i
                break

        self.loop = loop
        self.done = False

        self.curr_frame = 0
        self.frame_timer = 0

    def reset(self):
        self.done = False

        self.curr_frame = 0
        self.frame_timer = 0

    def update(self):
        if self.done:
            return True

        self.frame_timer += 1
        if self.frame_timer > self.anim_speed:
            self.frame_timer = 0
            self.curr_frame += 1
            if self.curr_frame >= self.anim_length:
                if self.loop:
                    self.curr_frame = 0
                else:
                    self.done = True
                    self.curr_frame -= 1

        return self.done

    def get_img(self):
        return self.imgs[self.curr_frame]


class Tileset:
    def __init__(self, sheet, tile_size=16):
        self.sheet = sheet
        self.tile_size = tile_size

        self.tile_amount = 0
        self.tiles = self._cut_tiles()

    def _cut_tiles(self):
        tiles = []

        self.tile_amount = self.sheet.width // self.tile_size
        for num in range(self.tile_amount):
            x = num * self.tile_size

            img = pygame.Surface([self.tile_size, self.tile_size], pygame.SRCALPHA)
            img.blit(self.sheet, [0, 0], [x, 0, self.tile_size, self.tile_size])

            tiles.append(img)

        return tiles

    def get_tile(self, idx):
        if idx > self.tile_amount:
            print("Tile index greater than length of tile list")
            return None
        return self.tiles[idx]