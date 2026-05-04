import pyxel
import math
import datetime as dt # for slime variants

# create enemy spawner coordinates, use random, and
# Work in progress

current_month = dt.datetime.now().month
#current_month = 9 # TO TEST THINGS ONLY

class Enemy:
    """The parent class for all enemy sprites"""
    img = 0
    width = 8
    height = 8

    def __init__(self, x_coord, y_coord):
        """Initializes parent class of Enemy"""
        self.x = x_coord
        self.y = y_coord
        self.is_alive = True
        self.hit_timer = 0

        # Default stats, child classes override
        self.hps = 10
        self.dmg = 3
        self.spd = 0.8
        self.aggro_radius = 48

    def take_damage(self, amount):
        """Handles death state for enemy sprites"""
        self.hps -= amount
        # add a 'hit' timer here for a visual flicker
        if self.hps <= 0:
            self.is_alive = False
        else:
            pass # simple knockback

    def update(self, player, is_night=False):
        """Defines the standard behavior for enemy sprites"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if self.hit_timer > 0:
            self.hit_timer -= 1

        # Aggro radius: Only moves within 48 pixels (6 tiles)
        if 0 < distance < self.aggro_radius:
            self.x += (dx / distance) * self.spd
            self.y += (dy / distance) * self.spd

        # Collision damage to player
        if distance < 8:
            # per 30fps
            player.hps -= (self.dmg / 30.0)

    def draw(self, cam_x, cam_y):
        """This will be overridden by child classes"""
        pass

class Oculus(Enemy):
    """Creates the enemy sprite Oculus"""
    def __init__(self, x, y):
        """Initializes class Oculus"""
        super().__init__(x, y)
        self.spd = 0.8
        self.u = 32
        self.v = 176

    def update(self, player, is_night=False):
        """We're overriding this method to provide buffs during night cycle"""
        if is_night:
            self.spd = 1
            self.aggro_radius = 72
            self.dmg = 5
            self.u = 40
            self.v = 184
        else:
            self.spd = 0.8
            self.aggro_radius = 48
            self.dmg = 3
            self.u = 32
            self.v = 176
        super().update(player, is_night)

    def draw(self, cam_x, cam_y):
        """Draws enemy sprite including a flicker effect once damaged"""
        if self.hit_timer > 0:
            # Swaps all colors to red (8) temporarily
            for i in range(16):
                pyxel.pal(i, 8) #col1=initial color, col2=final color

        pyxel.blt(self.x - cam_x, self.y - cam_y, 1,
                  self.u, self.v, 8, 8, 7)

        if self.hit_timer > 0:
            pyxel.pal()

class Slime(Enemy):
    """Creates the enemy sprite Slime"""
    def __init__(self, x, y):
        """Initializes class Slime"""
        super().__init__(x, y)
        self.spd = 0.5
        self.hps = 15
        self.dmg = 5
        self.u = 32
        self.v = 192

        # ----- Seasonal Sprite Logic! -----
        if current_month in [12, 1, 2]:
            # Winter: Dec, Jan, Feb -> 12,1,2
            self.u = 40
            self.v = 200
        elif current_month in [9, 10, 11]:
            # Autumn: Sep,Oct,Nov -> 9,10,11
            self.u = 32
            self.v = 200
        elif current_month in [6, 7, 8]:
            # Summer: Jun,Jul,Aug -> 6,7,8
            self.u = 40
            self.v = 192
        else: # Standard green
            self.u = 32
            self.v = 192

    def draw(self, cam_x, cam_y):
        """Draws the Slime with a damage flicker effect"""
        if self.hit_timer > 0:
            for i in range(16):
                pyxel.pal(i, 11) # flashes green
        pyxel.blt(self.x - cam_x, self.y - cam_y, 1,
                  self.u, self.v, 8, 8)