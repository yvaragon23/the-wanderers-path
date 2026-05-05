### Overview

"The Wanderer's Path" is a 2D top-down RPG built with Python and the Pyxel engine. 
The player can explore the map, battle enemies, and uncover hidden areas in a world
that dynamically responds to real-world weather and time.

#### 🌟 Features
* **Weather System:** Integrates with the OpenWeatherMap API to fetch real-world data.
If it rains in the real world, it rains in the game (and slows player movement).
Cooler temperatures spawn environmental anomalies like the mysterious fog which blocks
access to a part of the map.
* **Day/Night Cycle:** Reads your local system clock to alter environmental sprites and
buffs enemy stats during the night.
* **Seasonal Variants:** The slime enemy changes design based on the season
* **Action Combat:** Features melee basics and an unlockable AoE magic tied to a mana system
* **Interactive Environment:** Search the map for signs, unlocked entrances, and the key
to win the game


### Tutorial

In The Wanderer's Path, you play the character of The Wanderer and have the immediate option of movement
using the WASD keys as well as the arrow keys on your computer. You can use the space bar for
a basic attack on any enemies that come your way. You're able to view your stats via your
Heads-Up Display or HUD. You can toggle this on or off with your "H" key as explained in the menu screen.

Once spawned in, move your player along the path designed for you. Viewable enemies will come rushing
at you from a certain distance so be careful. You will have audio cues when you land damage on an enemy.
Although you are unable to see their health, know they are taking damage when your hear the audio
cue. The path ahead sometimes requires an objective to be fulfilled prior to moving onto 
the next obstacle. You will have prompts available once close enough to an entrance or sign so don't
be shy to explore! You win the game once you acquire the "key" available at the end.
Start by running the game in python run.py file.

NOTE: If you lose or win, you do NOT need to restart the program to play the game again!
Simply follow the instructions on screen

#### 🎮 Controls
* **Movement:** `W A S D` or `Arrow Keys`
* **Interact/Take/Enter:** `E` or `F` (it'll prompt you)
* **Basic Attack:** `SPACEBAR`
* **Cast Spell (AoE):** `R` (Requires Spell Tome & 5 Mana)
* **Toggle HUD:** `H`
* **Quit Game:** `L`


### Installation Instructions


To play The Wanderer's Path, you will need Python installed on your computer.
1. Ensure you have Python installed (3.7 or higher recommended!)
2. Ensure you have Pyxel 2.8.2 installed
3. Download or clone this repository to your computer
4. Start by running the game in python run.py

### Citation
[Tiny Town from Kenney!](https://kenney.nl/assets/tiny-town)
