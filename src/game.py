import pyxel
import math
import os #used to access the resource editor
import random
import datetime #used for day/night cycle

from src.simulation.weather_api import WeatherSim
from credentials import api_key
from src.player import Player
from src.world import World, get_tile_id, get_grid_coord
from src.enemy import Oculus, Slime

cam_x = 0
cam_y = 0

class Game:
    """Game class that handles both game logic and drawing."""
    def __init__(self):
        """Sets up the window for now"""
        pyxel.init(256, 144, title="The Wanderer's Path")
        base_path = os.path.dirname(os.path.dirname(__file__))
        asset_path = os.path.join(base_path, "assets", "assets.pyxres")
        pyxel.load(asset_path) # the above was needed to load the resource editor

        # Empty attributes
        self.state = "menu"
        self.world = None
        self.player = None
        self.enemies = []

        self.at_door1 = False
        self.door1_open = False
        self.in_house = False
        self.book_collected = False
        self.at_book = False
        self.at_exit1 = False

        self.at_door3 = False
        self.key_collected = False
        self.at_key = False
        self.key_grid_x = 65
        self.key_grid_y = 18

        # ------------------------ SIMULATION ------------------------
        self.weather = WeatherSim(api_key, city="Marietta")
        self.weather.fetch()
        #self.weather.condition = "Rain" #TO TEST THINGS ONLY
        #self.weather.temperature = 72.0 #TO TEST THINGS ONLY
        self.rain_particles = []

        self.at_sign = False
        self.fog = False
        self.at_fog_entrance = False
        self.at_fog_exit = False
        self.potion_drunk = False
        self.at_potion = False

        self.is_night = True

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """Resets the game state"""
        # Instantiate world and player
        self.world = World(pyxel.tilemaps[0])
        self.player = Player(self.world)
        self.enemies.clear()

        # Reset all one-time event flags!
        self.key_collected = False
        self.door1_open = False
        self.potion_drunk = False

        # Create enemy sprites
        self.enemies.append(Oculus(33 * 8, 8 * 8))
        self.enemies.append(Oculus(36 * 8, 10 * 8))
        self.enemies.append(Slime(61 * 8, 15 * 8 ))
        self.enemies.append(Slime(70 * 8, 21 * 8))

        # DAY/NIGHT CYCLE
        current_hour = datetime.datetime.now().hour
        # 20-24 means 8-11:59pm | 1-5:59am means just that
        if current_hour >= 20 or current_hour < 6:
            self.is_night = True
        else: self.is_night = False

        # Transition back into game state
        self.state = "game"


    # ------------------------ UPDATE ------------------------
    def update_camera(self):
        """Updates the camera position"""
        global cam_x, cam_y

        # Static camera for house scene
        if self.in_house:
            # Locks the camera exactly on the center of the dark room.
            cam_x = (16 * 8) - (pyxel.width // 2)
            cam_y = (32 * 8) - (pyxel.height // 2)
            return  # This stops the rest of the camera logic from running!

        # Centers camera on player
        cam_x = self.player.x - pyxel.width // 2
        cam_y = self.player.y - pyxel.height // 2
        # Clamp to world bounds
        cam_x = max(0, min(cam_x, 2728 - pyxel.width))
        cam_y = max(0, min(cam_y, 1024 - pyxel.height))

    def update(self):
        """Updates the game state"""
        if self.state == "menu":
            self.update_menu()
        elif self.state == "game_over":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
        elif self.state == "game_won":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
        else:
            self.update_game()

    def update_menu(self):
        """Updates the menu"""
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.reset_game()
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

    def update_house(self, p_grid_x, p_grid_y):
        """Handles all logic regarding the inside of the house"""
        # Exit of the house
        if 4 <= p_grid_x <= 6 and 30 <= p_grid_y <= 32:
            self.at_exit1 = True
            if pyxel.btnp(pyxel.KEY_Y):
                # Teleports to the outside.
                self.player.x = 36 * 8
                self.player.y = 6 * 8
                self.in_house = False
                self.at_exit1 = False
        else: self.at_exit1 = False

        # Allows collection of the "Spell Tome"
        if not self.player.has_item("Spell Tome"):
            # Measure from center of player to center of book (+8 pixels to X and Y)
            b_dx = (self.player.x + 8) - (get_grid_coord(22) + 8)
            b_dy = (self.player.y + 8) - (get_grid_coord(30) + 8)

            if math.sqrt(b_dx ** 2 + b_dy ** 2) < 24:  # Within 3 tiles
                self.at_book = True
                if pyxel.btnp(pyxel.KEY_F):
                    self.player.add_item("Spell Tome")
                    self.at_book = False
                    self.player.hps = self.player.mhp

                    # Replaces fence tiles with grass tileset
                    for x in range(46, 48): #Horizontal tile ID from 46-47
                        for y in range(5, 11): #Vertical tile ID from 5-10
                            pyxel.tilemaps[0].pset(x, y, (0, 0))
            else:
                self.at_book = False

    def update_weather(self):
        """Handles the weather-related mechanics and particle rain"""
        if self.weather.condition in ["Rain", "Drizzle", "Thunderstorm"] and not self.in_house:
            self.player.spd = 0.5 # muddy ground

            # rain particles
            if len(self.rain_particles) < 100: # limits the amount of rain particles
                self.rain_particles.append([random.randint(0, 256),
                                            random.randint(-144, 0)])
            for drop in self.rain_particles:
                drop[0] -= 1 # wind blowing left
                drop[1] += 4 # falling speed
                if drop[1] > 144:
                    drop[0] = random.randint(0, 256)
                    drop[1] = random.randint(-20, 0)
        if self.weather.temperature < 70.0:
            self.fog = True
        else:
            self.player.spd = 1.0 # resets speed

    def update_game(self):
        """Moves the player around via arrow keys or WASD keys.
        Defines certain controls, generates enemies, and
        decides teleportation spots in the map"""
        # --- UPDATES---
        self.update_weather()
        self.player.update()

        # --- PLAYER MOVEMENT & CAMERA ---
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.player.move_left()
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.player.move_right()
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.player.move_up()
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.player.move_down()

        self.update_camera()
        p_grid_x, p_grid_y = self.player.get_grid_pos()

        # --- COMBAT LOGIC ---
        if pyxel.btn(pyxel.KEY_SPACE): # Player basic attack
            self.player.basic_attack(self.enemies)

        if self.player.has_item("Spell Tome") and pyxel.btnp(pyxel.KEY_R):
            self.player.cast_spell(self.enemies)
                #pyxel.play()

        # --- ENEMY SPAWN---
        for enemy in self.enemies[:]:
            # The [:] creates a new, shallow copy of the list
            enemy.update(self.player, self.is_night)
            if not enemy.is_alive:
                print(enemy)
                self.enemies.remove(enemy)

        # --- DOOR ONE---
        if len(self.enemies) <= 2 and not self.door1_open and not self.in_house:
            self.door1_open = True

            # Tiles are counted 4x4 pixels. The door is 16x16 pixels
            # so we need to replace 4 tiles. This gets rid of the fence.
            pyxel.tilemaps[0].pset(36, 4, (get_tile_id(16), get_tile_id(112)))
            pyxel.tilemaps[0].pset(37, 4, (get_tile_id(24), get_tile_id(112)))
            pyxel.tilemaps[0].pset(36, 5, (get_tile_id(16), get_tile_id(120)))
            pyxel.tilemaps[0].pset(37, 5, (get_tile_id(24), get_tile_id(120)))

        # --- PROXY FOR DOOR ---
        if self.door1_open and not self.in_house:
            # Checks if player is near the 2x2 door (grids x: 35-36, y: 3-4)
            if 34 <= p_grid_x <= 37 and 2 <= p_grid_y <= 5:
                self.at_door1 = True

                # Wait for player input
                if pyxel.btnp(pyxel.KEY_E):
                    # Teleport!
                    self.player.x = get_grid_coord(6)
                    self.player.y = get_grid_coord(31)
                    self.in_house = True
                    self.at_door1 = False
                elif pyxel.btnp(pyxel.KEY_N):
                    # Nudge the player down slightly so they don't get stuck triggering it
                    self.player.y += 16
        else: self.at_door1 = False

        # --- INSIDE HOUSE ---
        if self.in_house:
            self.update_house(p_grid_x, p_grid_y)

        # --- PROXY FOR SIGN ---
        if 100 <= p_grid_x <= 103 and 8 <= p_grid_y <= 11:
            self.at_sign = True
        else: self.at_sign = False

        # --- PROXY FOR FOG ENTRANCE ---
        if not self.fog and (109 <= p_grid_x <= 113 and 11 <= p_grid_y <= 15):
            #^needs to be one line
                self.at_fog_entrance = True
                if pyxel.btnp(pyxel.KEY_E):
                    self.player.x = 0
                    self.player.y = 83 * 8
                    self.at_fog_entrance = False
        else: self.at_fog_entrance = False

        # --- PROXY FOR FOG EXIT ---
        if 0 <= p_grid_x <= 2 and 80 <= p_grid_y <= 83:
            self.at_fog_exit = True

            if pyxel.btnp(pyxel.KEY_E):
                # Teleports you back to the main map near the sign
                self.player.x = 108 * 8
                self.player.y = 13 * 8
                self.at_fog_exit = False
        else: self.at_fog_exit = False

        # --- POTION MECHANICS ---
        if not self.potion_drunk:
            # Measure distance to tile (14, 85)
            pot_dx = (self.player.x + 8) - ((14 * 8) + 4)
            pot_dy = (self.player.y + 8) - ((85 * 8) + 4)

            if math.sqrt(pot_dx ** 2 + pot_dy ** 2) < 24:
                self.at_potion = True
                if pyxel.btnp(pyxel.KEY_E):
                    self.potion_drunk = True
                    self.player.mhp += 10 #max hp up to 30
                    self.player.hps = self.player.mhp # full heal
                    self.at_potion = False
            else:
                self.at_potion = False

        # --- KEY & WIN STATE ---
        if len(self.enemies) == 0 and not self.key_collected:
            k_dx = (self.player.x + 8) - ((self.key_grid_x * 8) + 4)
            k_dy = (self.player.y + 8) - ((self.key_grid_y * 8) + 4)

            if math.sqrt(k_dx ** 2 + k_dy ** 2) < 24:
                self.at_key = True
                if pyxel.btnp(pyxel.KEY_E):
                    self.key_collected = True
                    self.state = "game_won"  # TRIGGER THE ENDING!
                    self.at_key = False
            else: self.at_key = False
        else: self.at_key = False

        # --- PLAYER HUD ---
        if pyxel.btnp(pyxel.KEY_H):
            self.player.show_hud = not self.player.show_hud

        # --- PLAYER LEAVE ---
        if pyxel.btn(pyxel.KEY_L):
            pyxel.quit()

        # --- PLAYER DIES & LOSS STATE ---
        if self.player.hps <= 0:
            self.state = "game_over"

    # ------------------------ DRAW ------------------------
    def draw(self):
        """Controls what is currently displayed"""
        pyxel.cls(0)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "game_won":
            self.draw_game_won()
        else:
            self.draw_game()

    @staticmethod
    def draw_menu():
        """Draws the menu"""
        title = "THE WANDERER'S PATH"
        pyxel.text(90, 20, title, 10)
        pyxel.text(84, 50, "WASD or Arrows to Move", 7)
        pyxel.text(98, 60, "SPACE to Attack", 7)
        pyxel.text(94, 70, "'H' to toggle HUD", 7)
        pyxel.text(94, 80, "'L' to leave game", 7)

        pyxel.text(88, 100, "Press ENTER to START", 7)

    @staticmethod
    def draw_game_won():
        """Draws the winning screen"""
        pyxel.text(112, 50, "YOU WON!", 11)
        pyxel.text(78, 70, "Congratulations wanderer!", 7)
        pyxel.text(78, 80, "Press ENTER to Play Again", 7)

    @staticmethod
    def draw_game_over():
        """Draws the death screen"""
        pyxel.text(110, 50, "GAME OVER", 8)
        pyxel.text(94, 70, "'L' to leave game", 7)
        pyxel.text(84, 80, "Press ENTER to RESTART", 7)

    def draw_house(self):
        """Handles all rendering to the inside of the house"""
        if not self.player.has_item("Spell Tome"):
            pyxel.blt(get_grid_coord(22) - cam_x, get_grid_coord(31) - cam_y, 1,
                      192, 112, 16, 16, 6)
        # Draw prompts
        if self.at_exit1:
            prompt_x = self.player.x - cam_x - 24
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 40, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Exit? Y/N", 7)

        if self.at_book:
            prompt_x = self.player.x - cam_x - 28
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 67, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Press F to Take", 7)

        if self.in_house and self.player.has_item("Spell Tome"):
            pyxel.rect(20, 120, 216, 15, 0)
            pyxel.rectb(20, 120, 216, 15, 7)
            pyxel.text(20 + 8, 120 +5, "Spell unlocked: AoE Blast! (Press 'R')", 10)

    def draw_fog(self):
        """Draws the fog for the secret level"""
        if self.fog:
            # 1. Grid (98, 1) - Normal
            pyxel.blt((98 * 8) - cam_x, (1 * 8) - cam_y, 1,
                      224, 16, 32, 16, 8)
            # 2. Grid (103, 5) - FLIPPED
            pyxel.blt((103 * 8) - cam_x, (5 * 8) - cam_y, 1,
                      224, 16, -32, 16, 8)
            # 3. Grid (105, 19) - Normal
            pyxel.blt((105 * 8) - cam_x, (19 * 8) - cam_y, 1,
                      224, 16, 32, 16, 8)

            # 4. Grid (97, 22) - Normal
            pyxel.blt((97 * 8) - cam_x, (22 * 8) - cam_y, 1,
                      224, 16, 32, 16, 8)
            # 5. Grid (110, 12) - FLIPPED
            pyxel.blt((110 * 8) - cam_x, (12 * 8) - cam_y, 1,
                      224, 16, -32, 16, 8)

    def draw_weather(self):
        """Handles rendering of weather overlays"""
        if self.weather.condition == "Rain" and not self.in_house:
            for drop in self.rain_particles:
                # Color 12 = Blue | pyxel.line(x1, y1, x2, y2, color)
                pyxel.line(drop[0], drop[1], drop[0] + 1, drop[1] + 3, 12)

    def draw_night_cycle(self):
        """Handles rendering of night-only graphics"""
        if self.is_night:
            # 1. Grid (16, 10)
            night_mush_u = 192
            night_mush_v = 64
            pyxel.blt((16 * 8) - cam_x, (10 * 8) - cam_y, 1,
                      night_mush_u, night_mush_v, 16, 16)
            # 2. Grid (59, 12)
            pyxel.blt((59 * 8) - cam_x, (12 * 8) - cam_y, 1,
                      night_mush_u, night_mush_v, 16, 16)
            # 3. Grid (105, 13)
            pyxel.blt((105 * 8) - cam_x, (13 * 8) - cam_y, 1,
                      night_mush_u, night_mush_v, 16, 16)

    def draw_game(self):
        """Draws the game"""
        # 1. Background
        pyxel.bltm(-cam_x, -cam_y, 0, 0, 0, 1024, 1024)

        # 2. Enemy sprites
        for enemy in self.enemies:
            # Uses the enemy's draw method, but adjusts for camera
            enemy.draw(cam_x, cam_y)

        # Draws key
        if len(self.enemies) == 0 and not self.key_collected:
            pyxel.blt((self.key_grid_x * 8) - cam_x, (self.key_grid_y * 8) - cam_y, 1,
                      144, 144, 16, 16, 0)

        # for the potion
        if not self.potion_drunk:
            # Full Potion: u=176, v=160
            pyxel.blt((15 * 8) - cam_x, (85 * 8) - cam_y, 1,
                      176, 160, 16, 16, 8)
        else:
            # Empty Bottle: u=160, v=160
            pyxel.blt((15 * 8) - cam_x, (85 * 8) - cam_y, 1,
                      160, 160, 16, 16, 8)

        # 3. Player sprite
        if self.player.facing == "left":
            u = self.player.u_left
            v = self.player.v_left
        else:
            u = self.player.u_right
            v = self.player.v_right
        pyxel.blt(self.player.x - cam_x, self.player.y - cam_y, self.player.img,
                  u, v, self.player.width, self.player.height, 8)

        # 5. In House drawings
        if self.in_house:
            self.draw_house()

        # ----------------------- PROMPTS -----------------------
        if self.at_door1:
            # Displays slightly above the player sprite
            prompt_x = self.player.x - cam_x - 12
            prompt_y = self.player.y - cam_y - 10
            pyxel.rect(prompt_x - 2, prompt_y - 2, 67, 9, 0)  # Black background
            pyxel.text(prompt_x, prompt_y, "Press E to Enter", 7)

        if self.at_key:
            prompt_x = self.player.x - cam_x - 24
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 70, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Press E to Take", 7)

        if self.at_fog_entrance and not self.fog:
            prompt_x = self.player.x - cam_x - 20
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 70, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Press E to Enter", 7)

        if self.at_sign:
            prompt_x = self.player.x - cam_x - 50
            prompt_y = self.player.y - cam_y - 14
            # Draws a wider black box for the message
            pyxel.rect(prompt_x - 2, prompt_y - 2, 127, 11, 0)

            # The message
            if self.fog:
                pyxel.text(prompt_x, prompt_y,
                           "WARNING: Weather Anomaly Active",8)
            else:
                pyxel.text(prompt_x, prompt_y,
                           "The anomaly has subsided...",7)

        if self.at_potion:
            prompt_x = self.player.x - cam_x - 24
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 70, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Press E to Drink", 11)

        if self.at_fog_exit:
            prompt_x = self.player.x - cam_x - 24
            prompt_y = self.player.y - cam_y - 12
            pyxel.rect(prompt_x - 2, prompt_y - 2, 70, 9, 0)
            pyxel.text(prompt_x, prompt_y, "Press E to Leave", 7)

        self.draw_weather()
        self.draw_fog()
        self.draw_night_cycle()
        self.player.draw_spell(cam_x, cam_y)

        # SIMPLE HUD
        if self.player.show_hud:
            #pyxel.text(2, 2,  f"Health: {self.player.hps} / {self.player.mhp}", 7)
            #pyxel.text(2, 10, f"Damage: {self.player.dmg}", 7)
            #pyxel.text(2, 18, f"Endurance: {self.player.end}", 7)
            #pyxel.text(2, 26, f"Inventory: {len(self.player.inventory)} items", 7)
            # Draw Health Bar
            bar_max_width = 40
            current_width = (self.player.hps / self.player.mhp) * bar_max_width

            # Background ()
            pyxel.rect(0, 0, 65, 9, 0)
            pyxel.rect(0, 8, 40, 15, 0)

            # Back frame (Dark Gray/13)
            pyxel.rect(2, 2, bar_max_width, 4, 13)
            # Forward frame (Red/8)
            pyxel.rect(2, 2, current_width, 4, 8)

            # Text overlay or other stats below it
            pyxel.text(45, 2, f"{int(self.player.hps)}/{self.player.mhp}", 7)
            pyxel.text(2, 8, f"Damage: {self.player.dmg}", 7)
            pyxel.text(2, 16, f"Mana: {self.player.mna}", 7)