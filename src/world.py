
solid_tiles = set()

def solid_area(x1, y1, x2, y2):
    """Takes pixel coordinates from the resource editor and adds
    the corresponding tiles to the solid_tiles set"""
    u1 = x1 // 8 # x-coord of upper left corner
    u2 = x2 // 8 # y-coord of upper left corner
    v1 = y1 // 8 # x-coord of lower right corner
    v2 = y2 // 8 # y-coord of lower right corner

    # add +1 because the upper bound is exclusive
    for u in range(min(u1, u2), max(u1, u2) + 1):
        for v in range(min(v1, v2), max(v1, v2) + 1):
            solid_tiles.add((u, v))

def get_tile_id(coord):
    """Takes a pixel coordinate and converts it to a tile id (row and column)"""
    result = coord // 8
    return result

def get_grid_coord(id):
    """Takes a tile id (row or column) and converts it to a grid coordinate"""
    result = id * 8
    return result

class World:
    """Creates a method used for collision"""
    # it is in tiles (8x8 pixels)
    height = 16
    width = 16

    def __init__(self, tilemap):
        """Initializes the world map and default player coordinates"""
        self.tilemap = tilemap
        self.player_grid_x = 0 #horizontal
        self.player_grid_y = 5 #vertical

    def is_wall(self, x, y):
        tile_y = int(y // 8)
        tile_x = int(x // 8)

        tile_cords = self.tilemap.pget(tile_x, tile_y)

        if tile_cords in solid_tiles:
            # THIS WILL SHOW YOU WHAT YOU ARE HITTING IN THE CONSOLE
            print(f"STUCK ON TILE: {tile_cords} at pixel {x},{y}")
            return True
        return False

"""Here, I have function calls which define game collision"""
# THE HOUSE - (0, 64)U(127, 111)
solid_area(0, 64, 127, 111)
# GREEN TREE UNIT CELL - (112, 16)U(127, 31)
solid_area(112, 16, 127, 31)
# YELLOW TREE UNIT CELL - (160, 16)U(175, 31)
solid_area(127, 31, 127, 31)
# HORIZONTAL STONE PILLARS TOP - (8, 128)U(39, 135)
solid_area(8, 128, 39, 135)
# GREEN TREE - (48, 0)U(191, 47)
solid_area(48, 0, 191, 47)
# VERTICAL WOODEN FENCE - (180, 50)U(187, 93)
solid_area(180, 50, 187, 93)
# HORIZONTAL WOODEN FENCE - (132, 98)U(171, 109)
solid_area(132, 98, 171, 109)
# IRON BRICKS - (96, 160)U(111, 175)
solid_area(96, 160, 111, 175)
# METAL ENTRANCE - (48, 144)U(70, 175)
solid_area(48, 144, 79, 175)
# IRON FLOOR - (0, 128)U(47, 175)
solid_area(0,128, 47, 175)