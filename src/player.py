import math
import pyxel

# needs to interact with enemy, have a basic attack that deals dmg
# to all enemies within a certain distance
# have a basic sprite attack to the player if the distance is small
class Player:
    """Class representing the player"""
    def __init__(self, world):
        """Initializes Player class with position, movement frames, stats
        inventory, and appropriate cooldowns"""
        self.world = world

        # Position
        self.x = world.player_grid_x * 8
        self.y = world.player_grid_y * 8
        self.img = 1
        self.width = 16
        self.height = 16
        #self.hitbox_w = 8
        #self.hitbox_h = 16

        # Player Frames
        self.u_left = 0
        self.v_left = 176
        self.u_right = 16
        self.v_right = 176
        self.facing = "left"

        # Core stats
        self.stats = {
            "MHP": 20, "HPS": 20,
            "DMG": 5, "END": 3,
            "SPD": 1, "MNA": 10
                      }

        self.lvl = 1
        self.mhp = 20 # max hit points
        self.hps = 20 # current hit points
        self.dmg = 5 # damage
        self.end = 3 # endurance
        self.mmn = 10
        self.mna = 10 # mana
        self.spd = 1 # speed

        self.dx = 1.25 * self.spd
        self.dy = 1.25 * self.spd

        # Skill points & Status effects
        self.points = 3
        self.status_effects = [] #burning, freezing, etc.

        # Inventory
        self.inventory = []
        self.show_hud = True

        self.attack_cooldown = 0
        self.magic_cooldown = 0
        self.spell_timer = 0
        self.spell_x = 0
        self.spell_y = 0



    # ------------------------ MOVEMENT ------------------------
    def can_move_to(self, new_x, new_y):
        """Checks if the player's hitbox would collide with a wall at new_x, new_y."""
        # We check the 4 corners of the 16x16 sprite.
        # To make it feel 'fair', we use a small margin so the player doesn't
        # get stuck on corners too easily.
        margin = 2

        corners = [
            (new_x + margin, new_y + margin),  # Top Left
            (new_x + self.width - margin, new_y + margin),  # Top Right
            (new_x + margin, new_y + self.height - margin),  # Bottom Left
            (new_x + self.width - margin, new_y + self.height - margin)  # Bottom Right
        ]

        for px, py in corners:
            if self.world.is_wall(px, py):
                return True  # There is a collision
        return False  # Path is clear

    # Defines player movement
    def move_left(self):
        """Moves the player left, both movement and image"""
        self.facing = "left"
        if not self.can_move_to(self.x - self.dx, self.y):
            self.x -= self.dx

    def move_right(self):
        """Moves the player right, both movement and image"""
        self.facing = "right"
        if not self.can_move_to(self.x + self.dx, self.y):
            self.x += self.dx

    def move_up(self):
        """Moves the player up"""
        if not self.can_move_to(self.x, self.y - self.dy):
            self.y -= self.dy

    def move_down(self):
        """Moves the player down"""
        if not self.can_move_to(self.x, self.y + self.dy):
            self.y += self.dy

    def get_grid_pos(self):
        """Returns the player's current X and Y position in grid coordinates"""
        # Adding 8 checks from the center of the 16x16 sprite
        grid_x = int((self.x + 8) // 8)
        grid_y = int((self.y + 8) // 8)
        return grid_x, grid_y

    # ------------------------ SKILL SYSTEM ------------------------
    def use_points(self, stat_name):
        """Allows for the player to build stats"""
        if self.points <= 0:
            return

        if stat_name == "damage":
            self.dmg += 1

        elif stat_name == "endurance":
            self.end += 1

        elif stat_name == "speed":
            self.spd += 1

        elif stat_name == "health":
            self.mhp += 2
            self.hps = min(self.hps + 2, self.mhp)

    # STATUS EFFECTS
    def add_status_effects(self, effect):
        """Method setup to keep track of status effects"""
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def remove_status_effects(self, effect):
        """Method setup to delete status effects"""
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    # INVENTORY
    def has_item(self, item_name):
        """Checks if the player has an item"""
        if item_name in self.inventory:
            return True
        else: return False

    def add_item(self, item_name):
        """Adds an item"""
        self.inventory.append(item_name)
    def remove_item(self, item_name):
        """Removes an item"""
        if item_name in self.inventory:
            self.inventory.remove(item_name)
        else:
            pass

    # ------------------------ COMBAT ------------------------
    def update(self):
        """Updates frame-by-frame player logic"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.magic_cooldown > 0:
            self.magic_cooldown -= 1

        if self.spell_timer > 0:
            self.spell_timer -= 1

        if pyxel.frame_count % 120 == 0:
            if self.hps < self.mhp:
                self.hps += 1
            if self.mna < self.mmn:
                self.mna += 1

    def basic_attack(self, enemies):
        """Checks if any enemies are in range and deals damage"""
        # Checks if on cooldown, if so the attack cannot be done
        if self.attack_cooldown > 0:
            return

        # Triggers a cooldown (30FPS)
        # 30 frames per 1 second, 15 frames per 0.5 seconds, 60 frames per 2 seconds
        self.attack_cooldown = 30

        for enemy in enemies:
            # This calculates the distance between player's center and enemy's center
            dx = (self.x + 8) - (enemy.x + 4) # local variable, not an attribute
            dy = (self.y - 8) - (enemy.y + 4)
            distance = math.sqrt(dx**2 + dy**2)
            # This deals the actual damage if within range
            if distance < 16:
                enemy.take_damage(self.dmg)
                pyxel.play(3, 0)

    def cast_spell(self, enemies):
        """AoE blast that costs mana and requires the Spell Tome"""
        if self.magic_cooldown > 0 or "Spell Tome" not in self.inventory or self.mna < 5:
            return False
        self.magic_cooldown = 60
        self.mna -= 5

        self.spell_timer = 20
        self.spell_x = self.x + 8
        self.spell_y = self.y + 8
        pyxel.play(2, 1)

        for enemy in enemies:
            dx = (self.x + 8) - (enemy.x + 4)
            dy = (self.y - 8) - (enemy.y + 4)
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Massive radius (40 pixels)
            if distance < 40:
                enemy.take_damage(self.dmg * 2)  # Spells hit twice as hard!
        return True  # Spell succeeded

    def draw_spell(self, cam_x, cam_y):
        """Draws the player's AoE Blast"""
        # The radius grows as the timer counts down
        if self.spell_timer > 0:
            current_radius = 40 - (self.spell_timer * 2)
            if current_radius > 0:
                # pyxel.circb(x, y, radius, color)
                # Outer purple ring then inner white ring
                pyxel.circb(self.spell_x - cam_x, self.spell_y - cam_y,
                            current_radius,2)
                pyxel.circb(self.spell_x - cam_x, self.spell_y - cam_y,
                            max(1, current_radius - 4), 7)