#!/usr/bin/env python
#
# plumpton is a Python text-based game library.
# Copyright (C) 2018 Thomas Woodcock <https://thomaswoodcock.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import inspect, tkinter, sys
from tkinter import font

PLUMPTON_VERSION = "0.1.0.a1"

class Trigger(object):
    """Simple event trigger."""

    def __init__(self):
        """Create an empty trigger object."""

        # Create subscribers set.
        self.subscribers = set()

    def subscribe(self, function):
        """Subscribe specified function to the trigger."""

        # Make sure function is callable.
        if callable(function):

            # Add to subcribers set.
            self.subscribers.add(function)

            # Log subscription.
            log(f"{function.__name__} subscribed to {self.__class__.__name__} {hex(id(self))}")

        else:

            # Log failed subscription.
            log(f"Could not subscribe '{function}' to {self.__class__.__name__} {hex(id(self))} (not callable)", "error")

    def unsubscribe(self, function):
        """Unsubscribe specified function from the trigger."""

        # Make sure function is subscribed.
        if function in self.subscribers:

            # Remove from subscribers set.
            self.subscribers.remove(function)

            # Log unsubscription.
            log(f"{function.__name__} unsubscribed from {self.__class__.__name__} {hex(id(self))}")

        else:

            # Log failed unsubscription.
            log(f"Could not unsubscribe '{function}' from {self.__class__.__name__} {hex(id(self))} (not subscribed)", "error")

    def __call__(self, *args, **kwargs):
        """Call all subscribed functions."""

        # Loop through subscribed functions.
        for function in self.subscribers:

            # Call each function, passing any arguments.
            function(*args, **kwargs)


class Game(object):
    """A collection of levels that form a game."""

    def __init__(self, name = "Game", speed = 25):
        """Create an empty game object."""

        # Creates levels list that holds the game's levels.
        self.levels = []

        # Check if name is at least one character in length.
        if len(str(name)) > 0:

            # Set name.
            self.name = str(name)

        else:

            # Set to default if not.
            self.name = "Game"

            # Log unsuccessful naming.
            log(f"Could not name {self.__class__.__name__} {hex(id(self))} (not valid length)", "error")

        # Check if game speed is at least zero.
        if int(speed) >= 0:

            # Set speed.
            self.speed = int(speed)

        else:

            # Set to default if not.
            self.speed = 25

            # Log unsuccessful speed set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} speed to '{speed}' (negative value)", "error")

        # Set default current level.
        self.current = None

        # Set Tkinter properties.
        self.tk = tkinter.Tk()
        self.tk.resizable(width = False, height = False)
        self.tk.title(self.name)
        self.window = tkinter.Canvas(self.tk, relief = "flat", bd = 0, highlightthickness = 0)

        # Register triggers.
        self.on_tick = Trigger()
        self.on_add = Trigger()
        self.on_remove = Trigger()
        self.on_empty = Trigger()
        self.on_run = Trigger()
        self.on_stop = Trigger()
        self.on_update = Trigger()

        # Log initialization.
        log(f"Initialized {self.__class__.__name__} {hex(id(self))} '{self.name}'")


    def __str__(self):
        """Return game name."""
        return self.name


    def add(self, level):
        """Adds the specified level to the game's level list."""

        # Check if level is in list.
        if not level in self.levels:

            # Ensure level is of valid type.
            if isinstance(level, Level):

                # Add to levels list.
                self.levels.append(level)

                # Set the level's game to this.
                level.game = self

                # Log add.
                log(f"Added {level.__class__.__name__} {hex(id(level))} to '{self.name}'")

                # Trigger on_add
                self.on_add()

            else:

                # Log unsuccessful add.
                log(f"Could not add '{level}' to '{self.name}' (not valid type)", "error")

        else:

            # Log unsuccessful add.
            log(f"Could not add {level.__class__.__name__} {hex(id(level))} to '{self.name}' (already a member)", "error")


    def remove(self, level):
        """Removes the specified level from the game's layer list."""

        # Check if level is in list.
        if level in self.levels:

            # Remove level from game.
            self.levels.remove(level)

            # Set level's game to none.
            level.game = None

            # Log remove.
            log(f"Removed {level.__class__.__name__} {hex(id(level))} from '{self.name}'")

            # Trigger on_remove
            self.on_remove()

        else:

            # Log unsuccessful remove.
            log(f"Could not remove '{level}' from '{self.name}' (not a member)", "error")


    def empty(self):
        """Removes all levels from the game's level list."""

        # Check if game has levels.
        if len(self.levels) > 0:

            # Change all levels' game to none.
            for level in self.levels:
                level.game = None

            # Clear levels list.
            self.levels.clear()

            # Log empty.
            log(f"Emptied '{self.name}'")

            # Trigger on_empty
            self.on_empty()

        else:

            # Log unsuccessful empty.
            log(f"Could not empty '{self.name}' (no members)", "error")

    def run(self, level):
        """Runs the specified game level."""

        # Check if level is running.
        if self.current != None:

            # Stop it if so.
            self.stop()

        # Check if level is in game's level list.
        if level in self.levels:

            # Make sure level is of valid type.
            if isinstance(level, Level):

                # Log run preparation.
                log(f"Preparing to run {level.__class__.__name__} {hex(id(level))} in '{self.name}'...")

                # Set current level.
                self.current = level

                # Clear window.
                self.window.delete("all")

                # Log text layering.
                log("Adding text layers to window...")

                # Load font.
                self.font = font.Font(family = self.current.font, size = self.current.font_size)

                # Create empty text layers list.
                self.textlayers = []

                # Loop through level's layers and create text layer for each.
                for layer in level.layers:

                    textlayer = self.window.create_text(0, 0, text = "", anchor = "nw",
                    font = self.font, fill = layer.font_colour)

                    # Add to text layers list.
                    self.textlayers.append(textlayer)

                # Log window configuration.
                log("Configuring window dimensions...")

                # Calculate window width and height.
                height = int(self.font.metrics("linespace")) * self.current.height
                width = int(self.font.measure(" ")) * self.current.width

                # Set window width and height.
                self.window.configure(bg = self.current.colour, width = width, height = height)
                self.window.pack(fill = "both", expand = "yes")

                # Log event preparation.
                log("Preparing key and mouse triggers...")


                # Manage tkinter events.
                def on_event(event):
                    """Parses tkinter event information and outputs formatted values."""

                    # Determine scroll direction.
                    if event.delta < 0:
                        direction = "Down"

                    elif event.delta > 0:
                        direction = "Up"

                    # Return none if no direction.
                    else:
                        direction = None

                    # Get mouse x and y.
                    xy = self.get_xy(event.x, event.y)

                    # Create dict for returning event data.
                    data = {"key_code": event.keycode,
                            "key_name": event.keysym,
                            "key_number": event.keysym_num,
                            "key_value": event.char,
                            "modifiers": get_modifiers(event.state),
                            "mouse_number": event.num,
                            "mouse_x": xy["x"],
                            "mouse_y": xy["y"],
                            "mouse_x_px": event.x,
                            "mouse_y_px": event.y,
                            "scroll_direction": direction}

                    # Check if event is mouse button press.
                    if str(event.type) == "ButtonPress":
                        self.current.on_mouse_down(data)

                    # Check if event is mouse button release.
                    elif str(event.type) == "ButtonRelease":
                        self.current.on_mouse_up(data)

                    # Check if event is mouse double click.
                    elif str(event.type) == "DoublePress" and (event.num == 1 or
                        event.num == 2 or event.num == 3):
                        self.current.on_mouse_down(data)
                        self.current.on_mouse_up(data)
                        self.current.on_mouse_double(data)

                    # Check if event is key double press.
                    elif str(event.type) == "DoublePress":
                        self.current.on_key_down(data)
                        self.current.on_key_up(data)
                        self.current.on_key_double(data)

                    # Check if event is mouse entering window.
                    elif str(event.type) == "Enter":
                        self.current.on_mouse_enter(data)

                    # Check if event is key press.
                    elif str(event.type) == "KeyPress":
                        self.current.on_key_down(data)

                    # Check if event is key release.
                    elif str(event.type) == "KeyRelease":
                        self.current.on_key_up(data)

                    # Check if event is mouse leaving window.
                    elif str(event.type) == "Leave":
                        self.current.on_mouse_leave(data)

                    # Check if event is mouse movement.
                    elif str(event.type) == "Motion":
                        self.current.on_mouse_move(data)

                    # Check if event is mouse wheel scroll.
                    elif str(event.type) == "MouseWheel":
                        self.current.on_mouse_scroll(data)

                    # Check if event is mouse triple click.
                    elif str(event.type) == "TriplePress" and (event.num == 1 or
                        event.num == 2 or event.num == 3):
                        self.current.on_mouse_down(data)
                        self.current.on_mouse_up(data)
                        self.current.on_mouse_triple(data)

                    # Check if event is key triple press.
                    elif str(event.type) == "TriplePress":
                        self.current.on_key_down(data)
                        self.current.on_key_up(data)
                        self.current.on_key_triple(data)


                # Parse tkinter's key modifiers.
                def get_modifiers(state):
                    """Parses the key modifiers from the tkinter event."""

                    # Create empty modifier list.
                    modifiers = []

                    # Check if shift pressed.
                    if state & 1:
                        modifiers.append("Shift")

                    # Check if caps lock enabled.
                    if state & 2:
                        modifiers.append("Caps Lock")

                    # Check if control pressed.
                    if state & 4:
                        modifiers.append("Control")

                    # Check if num lock enabled.
                    if state & 8:
                        modifiers.append("Num Lock")

                    # Check if scroll lock enabled.
                    if state & 32:
                        modifiers.append("Scroll Lock")

                    # Check if left mouse pressed.
                    if state & 256:
                        modifiers.append("Left Mouse")

                    # Check if middle mouse pressed.
                    if state & 512:
                        modifiers.append("Middle Mouse")

                    # Check if right mouse pressed.
                    if state & 1024:
                        modifiers.append("Right Mouse")

                    # Check if (left) alt pressed.
                    if state & 131072:
                        modifiers.append("Alt")

                    # Return modifier list.
                    return modifiers


                # Manage double click/press events.
                def on_event_double(event):
                    """Detects and modifies tkinter double click/press events."""

                    # Modify event type.
                    event.type = "DoublePress"

                    # Pass modified event.
                    on_event(event)


                # Manage triple click/press events.
                def on_event_triple(event):
                    """Detects and modifies tkinter triple click/press events."""

                    # Modify event type.
                    event.type = "TriplePress"

                    # Pass modified event.
                    on_event(event)


                # Log key binding.
                log("Binding keys to triggers...")

                # Register keybinds to triggers.
                self.tk.bind("<KeyPress>", on_event)
                self.tk.bind("<KeyRelease>", on_event)
                self.tk.bind("<Double-KeyPress>", on_event_double)
                self.tk.bind("<Triple-KeyPress>", on_event_triple)
                self.tk.bind("<ButtonPress>", on_event)
                self.tk.bind("<ButtonRelease>", on_event)
                self.tk.bind("<Motion>", on_event)
                self.tk.bind("<Enter>", on_event)
                self.tk.bind("<Leave>", on_event)
                self.tk.bind("<MouseWheel>", on_event)
                self.tk.bind("<Double-Button>", on_event_double)
                self.tk.bind("<Triple-Button>", on_event_triple)

                # Log game start.
                log(f"Running {level.__class__.__name__} {hex(id(level))} in '{self.name}'...")

                # Prepare tick loop.
                def tick():
                    """Calls onTick trigger in a loop."""

                    # Trigger onTick
                    self.on_tick()

                    # Check if game speed is above 0.
                    if self.speed > 0:

                        # Update window if so.
                        self.update()

                        # Loop at rate of game speed.
                        self.tk.after(self.speed, tick)

                    else:

                        # Otherwise tick every millisecond.
                        self.tk.after(1, tick)


                # Start tick loop.
                self.tk.after(0, tick)

                # Trigger on_run.
                self.on_run()

                # Start game loop.
                self.tk.mainloop()

                # Log completion.
                log(f"Successfully stopped.")

            else:

                # Log invalid level type.
                log(f"Could not run '{level}' in {self.__class__.__name__} {hex(id(self))} (not valid type)", "error")

        else:

            # Log invalid member.
            log(f"Could not run '{level}' in {self.__class__.__name__} {hex(id(self))} (not a member)", "error")


    def stop(self):
        """Stops running the current level."""

        # Log stop preparation.
        log(f"Preparing to stop {self.current.__class__.__name__} {hex(id(self.current))} in '{self.name}'...")

        # Unbind keys.
        self.tk.unbind("<KeyPress>")
        self.tk.unbind("<KeyRelease>")
        self.tk.unbind("<Double-KeyPress>")
        self.tk.unbind("<Triple-KeyPress>")
        self.tk.unbind("<ButtonPress>")
        self.tk.unbind("<ButtonRelease>")
        self.tk.unbind("<Double-Button>")
        self.tk.unbind("<Triple-Button>")
        self.tk.unbind("<Motion>")
        self.tk.unbind("<Enter>")
        self.tk.unbind("<Leave>")
        self.tk.unbind("<MouseWheel>")

        # Log key unbinding.
        log("Keys unbound.")

        # Delete text layers.
        self.window.delete("all")

        # Log text layer deletion.
        log("Text layers removed from window.")

        # Set game's current level to none.
        self.current = None

        # Trigger on_stop.
        self.on_stop()

    def update(self):
        """Renders level and updates the text layers of the window."""

        # Check that window's text layers matches level's layers.
        if len(self.textlayers) == len(self.current.layers):

            # Render level.
            grids = self.current.render()

            # Loop through layers.
            for i in range(len(grids)):

                # Update respective text layers.
                self.window.itemconfig(self.textlayers[i], text = grid_to_string(grids[i]), fill = self.current.layers[i].font_colour)

            # Update window.
            self.window.update_idletasks()

            # Trigger on_update.
            self.on_update()

        else:

            # Log unsuccessful update.
            log(f"Could not render {self.current.__class__.__name__} {hex(id(self.current))} in '{self.name}'... (invalid number of members)", "error")


    def get_xy(self, px, py):
        """Gets the position in the game grid at the specified pixel."""

        # Check that co-ordinate is within window bounds.
        if (int(px) > 0 and int(px) <= self.tk.winfo_width() and int(py) > 0
        and int(py) <= self.tk.winfo_height()):

            # Calculate x and y.
            x = int(px) // int(self.font.measure(" "))
            y = int(py) // self.font.metrics("linespace")

            # Return position.
            return {"x": x, "y": y}

        else:

            # Log unsuccessful get position. DISABLED due to log spam.
            #log(f"Could not get coordinates of ({px}, {py}) in '{self.name}' (out of bounds)", "error")

            # Return zero position.
            return {"x": 0, "y": 0}


class Level(object):
    """A collection of layers that make up a game level."""

    def __init__(self, width, height, game = None, colour = "black", font = "Consolas",
                font_size = -20):
        """Creates an empty level object."""

        # Creates layers list that holds the level's layers.
        self.layers = []

        # Check that width is positive.
        if int(width) > 0:

            # Set width.
            self.width = int(width)

        else:

            # Set to default if not.
            self.width = 1

            # Log unsuccessful width set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} width to '{width}' (negative or zero value)", "error")

        # Check that height is positive.
        if int(height) > 0:

            # Set height.
            self.height = int(height)

        else:

            # Set to default if not.
            self.height = 1

            # Log unsuccessful width set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} height to '{height}' (negative or zero value)", "error")

        # Check that colour is not empty.
        if len(str(colour)) > 0:

            # Set colour.
            self.colour = str(colour)

        else:

            # Set to default if not.
            self.colour = "black"

            # Log unsuccessful colour set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} colour (invalid length)", "error")

        # Check that font is not empty.
        if len(str(font)) > 0:

            # Set font.
            self.font = str(font)

        else:

            #Set to default if not.
            self.font = "Consolas"

            # Log unsuccessful font set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} font (invalid length)", "error")

        # Check that font size is integer.
        if isinstance(font_size, int):

            # Set font size.
            self.font_size = int(font_size)

        else:

            # Set to default if not.
            self.font_size = -20

            # Log unsuccessful font size set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} font size to {font_size} (not valid type)", "error")

        # Check that game is valid type.
        if isinstance(game, Game):

            # Add level to game.
            game.add(self)

            # Set game.
            self.game = game

        else:

            # Set to default if not.
            self.game = None

            # Log unsuccessful game set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} game to {game} (not valid type)", "error")

        # Register key triggers.
        self.on_key_down = Trigger()
        self.on_key_up = Trigger()
        self.on_key_double = Trigger()
        self.on_key_triple = Trigger()

        # Register mouse triggers.
        self.on_mouse_down = Trigger()
        self.on_mouse_up = Trigger()
        self.on_mouse_double = Trigger()
        self.on_mouse_triple = Trigger()
        self.on_mouse_move = Trigger()
        self.on_mouse_enter = Trigger()
        self.on_mouse_leave = Trigger()
        self.on_mouse_scroll = Trigger()

        # Register triggers.
        self.on_add = Trigger()
        self.on_remove = Trigger()
        self.on_empty = Trigger()
        self.on_render = Trigger()

        # Log initialization.
        log(f"Initialized {self.__class__.__name__} {hex(id(self))} [{self.width}x{self.height}]")


    def __str__(self):
        """Return a string representation of level."""

        # Create empty grid for drawing.
        grid = build_shape(self.width, self.height)

        # Render layers.
        layers = self.render()

        # Loop through each row in grid.
        for row in range(self.height):

            # Loop through each column in row.
            for col in range(self.width):

                # Loop backwards through layers to find topmost character.
                for layer in range(len(self.layers) -1, -1, -1):

                    # Check if cell in grid contains character.
                    if layers[layer][row][col] != " ":

                        # Add value to current cell if so.
                        grid[row][col] = layers[layer][row][col]

                        # Stop rendering cell.
                        break

        # Return grids
        return grid_to_string(grid)


    def add(self, layer):
        """Adds the specified layer to the level's layer list."""

        # Check if layer is in list.
        if not layer in self.layers:

            # Ensure layer is of valid type.
            if isinstance(layer, Layer):

                # Add to layers list.
                self.layers.append(layer)

                # Set the layer's level to this.
                layer.level = self

                # Log add.
                log(f"Added {layer.__class__.__name__} {hex(id(layer))} to {self.__class__.__name__} {hex(id(self))}")

                # Trigger on_add.
                self.on_add()

            else:

                # Log unsuccessful add.
                log(f"Could not add '{layer}' to {self.__class__.__name__} {hex(id(self))} (not valid type)", "error")

        else:

            # Log unsuccessful add.
            log(f"Could not add {layer.__class__.__name__} {hex(id(layer))} to {self.__class__.__name__} {hex(id(self))} (already a member)", "error")


    def remove(self, layer):
        """Removes the specified layer from the level's layer list."""

        # Check if layer is in list.
        if layer in self.layers:

            # Remove layer from level.
            self.layers.remove(layer)

            # Set layer's level to none.
            layer.level = None

            # Log remove.
            log(f"Removed {layer.__class__.__name__} {hex(id(layer))} from {self.__class__.__name__} {hex(id(self))}")

            # Trigger on_remove.
            self.on_remove()

        else:

            # Log unsuccessful remove.
            log(f"Could not remove '{layer}' from {self.__class__.__name__} {hex(id(self))} (not a member)", "error")


    def empty(self):
        """Removes all layers from the level's layer list."""

        # Check if level has layers.
        if len(self.layers) > 0:

            # Change all layers' level to none.
            for layer in self.layers:
                layer.level = None

            # Clear layers list.
            self.layers.clear()

            # Log empty.
            log(f"Cleared {self.__class__.__name__} {hex(id(self))}")

            # Trigger on_empty.
            self.on_empty()

        else:

            # Log unsuccessful empty.
            log(f"Could not empty {self.__class__.__name__} {hex(id(self))} (no members)", "error")


    def render(self):
        """Generates grids by evaluating level's layers and their positions."""

        # Check if level has layers.
        if len(self.layers) > 0:

            # Create empty list of grids.
            grids = [build_shape(self.width, self.height) for layer in range(len(self.layers))]

            # Create empty list of layers and render each layer in the level.
            layers = []

            # Loop through layers.
            for layer in self.layers:

                # Create a grid for each layer.
                grid = build_shape(self.width, self.height)

                # Ensure layer is of valid type.
                if isinstance(layer, Layer):

                    # Loop through shapes.
                    for shape in layer.shapes:

                        # Ensure shape is of valid type.
                        if isinstance(shape, Shape):

                            # Loop through rows of shape's grid.
                            for row_i, row_v in enumerate(shape.grid):

                                # Loop through columns of row.
                                for col_i, col_v in enumerate(row_v):

                                    # Calculate character's position in level.
                                    y = row_i + layer.y + shape.y
                                    x = col_i + layer.x + shape.x

                                    # Check if character is visible in level.
                                    if (y >= layer.y and y < layer.height + layer.y and
                                    y < self.height and x >= layer.x and x < layer.width
                                    + layer.x and x < self.width):

                                        # Insert into grid if so.
                                        grid[y][x] = col_v

                    # Add grid to list.
                    layers.append(grid)

            # Loop through each row in level's grid.
            for row in range(self.height):

                # Loop through each column in row.
                for col in range(self.width):

                    # Loop backwards through layers to find topmost character.
                    for layer in range(len(self.layers) -1, -1, -1):

                        # Check if cell is whitespace.
                        if layers[layer][row][col] == " ":

                            # Add to grid layer.
                            grids[layer][row][col] = layers[layer][row][col]

                        else:

                            # Add to grid layer.
                            grids[layer][row][col] = layers[layer][row][col]

                            # Move onto the next cell.
                            break

            # Trigger on_render.
            self.on_render()

            # Return grids
            return grids

        else:

            # Log unsuccessful render.
            log(f"Could not render {self.__class__.__name__} {hex(id(self))} (no members)", "error")

            # Return empty list.
            return []

    def get_character(self, x, y):
        """Returns the topmost character at the specified position in the game grid."""

        # Check if position is within bounds.
        if x >= 0 and x < self.width and y >= 0 and y < self.height:

            # Render grids locally.
            grids = self.render()

            # Set default return character.
            character = " "

            # Loop through layers.
            for layer in range(len(grids)):

                # Check if character at location is whitespace.
                if grids[layer][y][x] != " ":

                    # Set return character as cell's value if so.
                    character = grids[layer][y][x]

            # Return last non-whitespace character.
            return character

        else:

            # Log unsuccessful get character.
            log(f"Could not get character at ({x}, {y}) in {self.__class__.__name__} {hex(id(self))} (out of bounds)", "error")

            # Return whitespace.
            return " "

    def get_shape(self, x, y):
        """Returns the topmost shape at the specified position in the game grid."""

        # Check if position is within bounds.
        if x >= 0 and x < self.width and y >= 0 and y < self.height:

            # Set default return shape.
            rshape = None

            # Loop through layers.
            for l in range(len(self.layers)):

                # Keep track of current layer.
                layer = self.layers[l]

                # Loop backwards through shapes on the layer.
                for s in range(len(layer.shapes)):

                    # Keep track of current shape.
                    shape = layer.shapes[s]

                    # Check if shape touches this location.
                    if (x < layer.x + shape.x + shape.width and x >= layer.x + shape.x
                    and y < layer.y + shape.y + shape.height and y >= layer.y + shape.y):

                        # Calculate character's local position in shape.
                        sx = x - layer.x - shape.x
                        sy = y - layer.y - shape.y

                        # Check that cell in grid is not empty.
                        if shape.grid[sy][sx] != " " or shape.opaque == True:

                            # Set as return shape if so.
                            rshape = shape

            # Return last shape.
            return rshape

        else:

            # Log unsuccessful get shape.
            log(f"Could not get shape at ({x}, {y}) in {self.__class__.__name__} {hex(id(self))} (out of bounds)", "error")

            # Return none.
            return None


class Layer(object):
    """A collection of shapes that reside on the same plane."""

    def __init__(self, width, height, x = 0, y = 0, level = None, font_colour = "white", edges = False):
        """Creates an empty layer object."""

        # Creates shapes list that holds the layer's shapes.
        self.shapes = []

        # Check that width is positive.
        if int(width) > 0:

            # Set width.
            self.width = int(width)

        else:

            # Set to default if not.
            self.width = 1

            # Log unsuccessful width set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} width to '{width}' (negative or zero value)", "error")

        # Check that height is positive.
        if int(height) > 0:

            # Set height.
            self.height = int(height)

        else:

            # Set to default if not.
            self.height = 1

            # Log unsuccessful height set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} height to '{height}' (negative or zero value)", "error")

        # Check that font colour is not empty.
        if len(str(font_colour)) > 0:

            # Set font colour.
            self.font_colour = str(font_colour)

        else:

            # Set to default if not.
            self.font_colour = "white"

            # Log unsuccessful font colour set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} font colour (invalid length)", "error")

        # Check that x position is integer.
        if isinstance(x, int):

            # Set x position.
            self.x = int(x)

        else:

            # Set to default if not.
            self.x = 0

            # Log unsuccessful x position set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} x position to '{x}' (not valid type)", "error")

        # Check that y position is integer.
        if isinstance(y, int):

            # Set y position.
            self.y = int(y)

        else:

            # Set to default if not.
            self.y = 0

            # Log unsuccessful y position set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} y position to '{y}' (not valid type)", "error")

        # Check that edges is bool.
        if isinstance(edges, bool):

            # Set edges.
            self.edges = bool(edges)

        else:

            # Set to default if not.
            self.edges = False

            # Log unsuccessful edges set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} edges to '{edges}' (not valid type)", "error")

        # Check that level is valid type.
        if isinstance(level, Level):

            # Add layer to level.
            level.add(self)

            # Set level.
            self.level = level

        else:

            # Set to default if not.
            self.level = None

            # Log unsuccessful level set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} level to '{level}' (not valid type)", "error")

        # Set triggers.
        self.on_add = Trigger()
        self.on_remove = Trigger()
        self.on_empty = Trigger()
        self.on_move = Trigger()
        self.on_render = Trigger()

        # Log initialization.
        log(f"Initialized {self.__class__.__name__} {hex(id(self))} at ({self.x}, {self.y}) [{self.width}x{self.height}]")


    def __str__(self):
        """Return a string representation of layer."""

        # Return layer string.
        return grid_to_string(self.render())


    def add(self, shape):
        """Adds the specified shape to the layer's shape list."""

        # Ensure shape is not in shapes list.
        if not shape in self.shapes:

            # Ensure shape is of valid type.
            if isinstance(shape, Shape):

                # Add to shapes list.
                self.shapes.append(shape)

                # Set shape's layer.
                shape.layer = self

                # Log add.
                log(f"Added {shape.__class__.__name__} {hex(id(shape))} to {self.__class__.__name__} {hex(id(self))}")

                # Trigger on_add.
                self.on_add()

            else:

                # Log invalid type.
                log(f"Could not add '{shape}' to {self.__class__.__name__} {hex(id(self))} (not valid type)", "error")

        else:

            # Log unsuccessful add.
            log(f"Could not add {shape.__class__.__name__} {hex(id(shape))} to {self.__class__.__name__} {hex(id(self))} (already a member)", "error")


    def remove(self, shape):
        """Removes the specified shape from the layer's shape list."""

        # Check if shape in shapes list.
        if shape in self.shapes:

            # Check if shape is valid type.
            if isinstance(shape, Shape):

                # Remove shape from layer.
                self.shapes.remove(shape)

                # Set shape's layer to none.
                shape.layer = None

                # Log remove.
                log(f"Removed {shape.__class__.__name__} {hex(id(shape))} from {self.__class__.__name__} {hex(id(self))}")

                # Trigger on_remove.
                self.on_remove()

            else:

                # Log incorrect type.
                log(f"Could not remove '{shape}' from {self.__class__.__name__} {hex(id(self))} (not valid type)", "error")

        else:

            # Log unsuccessful remove.
            log(f"Could not remove {shape.__class__.__name__} {hex(id(shape))} from {self.__class__.__name__} {hex(id(self))} (not a member)", "error")


    def empty(self):
        """Removes all shapes from the layer's shape list."""

        # Checks if layer has at least one shape.
        if len(self.shapes) > 0:

            # Loop through shapes.
            for shape in self.shapes:

                # Set all shapes' layer to none.
                shape.layer = None

            # Clear all shapes.
            self.shapes.clear()

            # Log empty.
            log(f"Emptied {self.__class__.__name__} {hex(id(self))}")

            # Trigger on_empty.
            self.on_empty()

        else:

            # Log unsuccessful empty.
            log(f"Could not empty {self.__class__.__name__} {hex(id(self))} (no members)", "error")


    def render(self):
        """Generates grid by evaluating layer's shapes and their positions."""

        # Check if layer has at least one shape.
        if len(self.shapes) > 0:

            # Create a blank grid to draw on.
            grid = build_shape(self.width, self.height)

            # Loop through shapes.
            for shape in self.shapes:

                # Ensure shape is of valid type.
                if isinstance(shape, Shape):

                    # Loop through rows of shape's grid.
                    for row_i, row_v in enumerate(shape.grid):

                        # Loop through columns of row.
                        for col_i, col_v in enumerate(row_v):

                            # Ensure character is visible within layer.
                            if (row_i + shape.y >= 0 and row_i + shape.y < self.height
                            and col_i + shape.x >= 0 and col_i + shape.x < self.width):

                                # Add character to blank grid if so.
                                grid[row_i + shape.y][col_i + shape.x] = col_v

            # Trigger on_render.
            self.on_render()

            # Return grid.
            return grid

        else:

            # Log unsuccessful render.
            log(f"Could not render {self.__class__.__name__} {hex(id(self))} (no members)", "error")

            # Return empty list.
            return []

    def get_character(self, x, y):
        """Returns the topmost character at the specified position in the layer."""

        # Check that coordinate is within bounds of layer.
        if x >= 0 and x < self.width and y >= 0 and y < self.height:

            # Render grids locally.
            grid = self.render()

            # Return character at location.
            return grid[y][x]

        else:

            # Log unsuccessful get character.
            log(f"Could not get character at ({x}, {y}) in {self.__class__.__name__} {hex(id(self))} (out of bounds)", "error")

            # Return whitespace.
            return " "

    def get_shape(self, x, y):
        """Returns the topmost shape at the specified position in the layer."""

        # Check that coordinate is within bounds of layer.
        if x >= 0 and x < self.width and y >= 0 and y < self.height:

            # Set default return shape.
            rshape = None

            # Loop through shapes on the layer.
            for s in range(len(self.shapes)):

                # Keep track of shape.
                shape = self.shapes[s]

                # Check if shape touches this location.
                if (x < shape.x + shape.width and x >= shape.x
                and y < shape.y + shape.height and y >= shape.y):

                    # Calculate character's local position in shape.
                    sx = x - shape.x
                    sy = y - shape.y

                    # Check that cell in grid is not empty.
                    if shape.grid[sy][sx] != " " or shape.opaque == True:

                        # Set return shape if not.
                        rshape = shape

            # Return shape.
            return rshape

        else:

            # Log unsuccessful get shape.
            log(f"Could not get shape at ({x}, {y}) in {self.__class__.__name__} {hex(id(self))} (out of bounds)", "error")

            # Return none.
            return None

    def set_position(self, x, y):
        """Moves the layer to the specified location in the level."""

        # Update x and y values.
        self.x = int(x)
        self.y = int(y)

        # Log position change.
        log(f"Moved {self.__class__.__name__} {hex(id(self))} to ({x}, {y}) in {self.level.__class__.__name__} {hex(id(self.level))}")

        # Trigger on_move
        self.on_move()


class Shape(object):
    """A graphical object of specified width and height that represents a
    collection of rows of characters."""

    def __init__(self, width, height, character = " ", x = 0, y = 0, layer = None, solid = False, opaque = False, direction = 0, speed = 0):
        """Creates an empty shape object."""

        # Creates grid attribute that holds list that makes up shape.
        self.grid = build_shape(width, height, character)

        # Check if width is positive.
        if int(width) > 0:

            # Set width.
            self.width = int(width)

        else:

            # Set to default if not.
            self.width = 1

            # Log unsuccessful width set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} width to '{width}' (negative or zero value)", "error")

        # Check if height is positive.
        if int(height) > 0:

            # Set height.
            self.height = int(height)

        else:

            # Set to default if not.
            self.height = 1

            # Log unsuccessful height set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} height to '{height}' (negative or zero value)", "error")

        # Check if x position is integer.
        if isinstance(x, int):

            # Set x position.
            self.x = int(x)

        else:

            # Set to default if not.
            self.x = 0

            # Log unsuccessful x position set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} x position to '{x}' (not valid type)", "error")

        # Check if y position is integer.
        if isinstance(y, int):

            # Set y position.
            self.y = int(y)

        else:

            # Set to default if not.
            self.y = 0

            # Log unsuccessful y position set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} y position to '{y}' (not valid type)", "error")

        # Check if solid is bool.
        if isinstance(solid, bool):

            # Set solid.
            self.solid = bool(solid)

        else:

            # Set to default if not.
            self.solid = False

            # Log unsuccessful solid set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} solid to '{solid}' (not valid type)", "error")

        # Check if opaque is bool.
        if isinstance(opaque, bool):

            # Set opaque.
            self.opaque = bool(opaque)

        else:

            # Set to default if not.
            self.opaque = False

            # Log unsuccessful opaque set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} opaque to '{opaque}' (not valid type)", "error")

        # Check if direction is None or between 0 and 7.
        if direction == None or (int(direction) >= 0 and int(direction) < 8):

            # If direction is None.
            if direction == None:

                # Set direction.
                self.direction = None

            else:

                # Set direction as integer.
                self.direction = int(direction)

        else:

            # Set to default if not.
            self.direction == None

            # Log unsuccessful direction set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} direction to '{direction}' (not valid value)", "error")

        # Check if speed is zero or positive.
        if int(speed) >= 0:

            # Set speed.
            self.speed = int(speed)

        else:

            # Set to default if not.
            self.speed = 0

            # Log unsuccessful speed set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} speed to '{speed}' (negative or zero value)", "error")

        # Check that layer is valid type.
        if isinstance(layer, Layer):

            # Add shape to layer.
            layer.add(self)

            # Set layer.
            self.layer = layer

        else:

            # Set to default if not.
            self.layer = None

            # Log unsuccessful layer set.
            log(f"Could not set {self.__class__.__name__} {hex(id(self))} layer to '{layer}' (not valid type)", "error")

        # Set frame counter for animations.
        self.frames = 0

        # Set triggers.
        self.on_draw = Trigger()
        self.on_erase = Trigger()
        self.on_fill = Trigger()
        self.on_empty = Trigger()
        self.on_write = Trigger()
        self.on_flip = Trigger()
        self.on_move = Trigger()
        self.on_collide = Trigger()
        self.on_hit_edge = Trigger()
        self.on_freeze = Trigger()
        self.on_stop = Trigger()
        self.on_reverse = Trigger()

        # Log initialization.
        log(f"Initialized {self.__class__.__name__} {hex(id(self))} at ({self.x}, {self.y}) [{self.width}x{self.height}]")


    def __str__(self):
        """Returns a string representation of the shape's grid."""

        # Return string grid.
        return grid_to_string(self.grid)


    def draw(self, character, width, height, x, y):
        """Inserts a rectangular area of characters into the shape's grid."""

        # Check that character has a length of one.
        if len(str(character)) == 1:

            # Check that width is positive.
            if int(width) > 0:

                # Check that height is positive.
                if int(height) > 0:

                    # Check that drawing will stay within bounds.
                    if x + width >= 0 and x + width <= self.width and y + height >= 0 and y + height <= self.height:

                        # Loop through rows of height.
                        for row in range(height):

                            # Loop through columns of row.
                            for col in range(width):

                                # Add character to shape.
                                self.grid[row + y][col + x] = character

                        # Log drawing.
                        log(f"Inserted '{character}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) [{width}x{height}]")

                        # Trigger on_draw
                        self.on_draw()

                    else:

                        # Log unsuccessful draw.
                        log(f"Could not insert '{character}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) [{width}x{height}] (out of bounds)", "error")

                else:

                    # Log negative or zero height.
                    log(f"Could not insert '{character}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) [{width}x{height}] (negative or zero height value)", "error")

            else:

                # Log negative or zero width.
                log(f"Could not insert '{character}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) [{width}x{height}] (negative or zero width value)", "error")

        else:

            # Log invalid character length.
            log(f"Could not insert '{character}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) [{width}x{height}] (not valid length)", "error")


    def erase(self, width, height, x, y):
        """Removes an area of characters in the shape's grid."""

        # Check that width is positive.
        if int(width) > 0:

            # Check that height is positive.
            if int(height) > 0:

                # Check that erasing will stay within bounds.
                if x + width >= 0 and x + width <= self.width and y + height >= 0 and y + height <= self.height:

                    # Use draw to insert whitespace.
                    self.draw(" ", width, height, x, y)

                    # Log erase.
                    log(f"Erased [{width}x{height}] from {self.__class__.__name__} {hex(id(self))} at ({x}, {y})")

                    # Trigger on_erase.
                    self.on_erase()

                else:

                    # Log unsuccessful erase.
                    log(f"Could not erase [{width}x{height}] from {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (out of bounds)", "error")

            else:

                # Log negative or zero height.
                log(f"Could not erase [{width}x{height}] from {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (negative or zero height value)", "error")

        else:

            # Log negative or zero width.
            log(f"Could not erase [{width}x{height}] from {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (negative or zero width value)", "error")


    def fill(self, character):
        """Fills the entirety of shape's grid with specified character."""

        # Check that character has a length of one.
        if len(str(character)) == 1:

            # Fill the grid.
            self.draw(character, self.width, self.height, 0, 0)

            # Log fill.
            log(f"Filled {self.__class__.__name__} {hex(id(self))} with '{character}'")

            # Trigger on_fill.
            self.on_fill()

        else:

            # Log invalid character length.
            log(f"Could not fill {self.__class__.__name__} {hex(id(self))} with '{character}' (not valid length)", "error")

    def empty(self):
        """Removes all characters from the shape's grid."""

        # Use fill to insert whitespace.
        self.fill(" ")

        # Log empty.
        log(f"Emptied {self.__class__.__name__} {hex(id(self))}")

        # Trigger on_empty.
        self.on_empty()


    def write(self, text, x = 0, y = 0, wrap = False):
        """Inserts text into the shape's grid at the specified position."""

        # Ensure text is not empty.
        if len(str(text)) > 0:

            # Ensure position is within bounds.
            if int(x) >= 0 and int(x) < self.width and int(y) >= 0 and int(y) < self.height:

                # Ensure wrap is bool.
                if isinstance(wrap, bool):

                    # Check if wrap is fale.
                    if wrap == False:

                        # Set max length to end of line if so.
                        max = self.width - x

                    else:

                        # Set max length to end of shape if true.
                        max = (self.height - y) * (self.width - x)

                    # Set starting indexes.
                    row = 0
                    col = 0

                    # Loop through text.
                    for char in range(min(max, len(text))):

                        # Check if reached end of row and wrapping.
                        if col == self.width - x and wrap == True:

                            # Increment row and set col back to start.
                            row += 1
                            col = 0

                        # Add to shape's grid and increment column.
                        self.grid[y + row][x + col] = text[char]
                        col += 1

                    # Check if managed to print all text.
                    if min(max, len(text)) == len(text):

                        # Log writing.
                        log(f"Write'{text}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y})")

                        # Trigger on_write.
                        self.on_write()

                    else:

                        # Log incomplete writing.
                        log(f"Could only write '{text[:max]}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (out of bounds)", "error")

                        # Trigger on_write.
                        self.on_write()

                else:

                    # Log invalid wrap.
                    log(f"Could not write '{text}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (not valid wrap type)", "error")

            else:

                # Log out of bounds.
                log(f"Could not write '{text}' into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (out of bounds)", "error")

        else:

            # Log invalid text length.
            log(f"Could not write into {self.__class__.__name__} {hex(id(self))} at ({x}, {y}) (not valid length)", "error")


    def flip(self, axis):
        """Flips the shape's grid on the x or y axis."""

        # Check if axis is x.
        if str(axis) == "x":

            # Copy grid.
            grid = list(self.grid)

            # Reverse grid.
            grid.reverse()

            # Set shape's grid.
            self.grid = grid

            # Trigger on_flip.
            self.on_flip()

        # Check if axis is y.
        elif str(axis) == "y":

            # Copy grid
            grid = list(self.grid)

            # Loop through rows of grid.
            for row in grid:

                # Reverse row.
                row.reverse()

            # Set shape's grid.
            self.grid = grid

            # Trigger on_flip.
            self.on_flip()

        else:

            # Log unsuccessful flip.
            log(f"Could not flip {self.__class__.__name__} {hex(id(self))} on '{axis}' axis (not valid value)", "error")


    def nearby(self, distance = 1, direction = None):
        """Detects adjacent shapes within a radius."""

        # Check that distance is positive.
        if int(distance) > 0:

            # Check that direction is None or between 0 and 5
            if direction == None or (direction >= 0 and direction < 6):

                # Create blank list of detected shapes.
                shapes = []

                # Calculate edges of current shape.
                edges = [self.width + self.x, self.height + self.y, self.x - 1, self.y - 1]

                # Get index of current layer to detect shapes above and below.
                index = self.layer.level.layers.index(self.layer)

                # If no direction entered.
                if direction == None:

                    # Loop through each direction.
                    for i in range(6):

                        # Get nearby in each direction.
                        shapes.append(self.nearby(distance, i))

                    # Return shapes.
                    return shapes

                # Loop through each step in radius.
                for step in range(int(distance)):

                    # Create list for each step.
                    steps = []

                    # If detecting to the right.
                    if direction == 0:

                        # Loop through each row of shape.
                        for row in range(self.height):

                            # Detect shapes outside of edge.
                            shape = self.layer.get_shape(edges[0] + step, self.y + row)

                            # Check if shape detected.
                            if shape != None:

                                # Add to list if so.
                                steps.append(shape)

                    # If detecting down.
                    elif direction == 1:

                        # Loop through each column of shape.
                        for col in range(self.width):

                            # Detect shapes outside of edge.
                            shape = self.layer.get_shape(self.x + col, edges[1] + step)

                            # Check if shape detected.
                            if shape != None:

                                # Add to list if so.
                                steps.append(shape)

                    # If detecting to the left.
                    elif direction == 2:

                        # Loop through each row of shape.
                        for row in range(self.height):

                            # Detect shapes outside of edge.
                            shape = self.layer.get_shape(edges[2] - step, self.y + row)

                            # Check if shape detected.
                            if shape != None:

                                # Add to list if so.
                                steps.append(shape)

                    # If detecting up.
                    elif direction == 3:

                        # Loop through each column of shape.
                        for col in range(self.width):

                            # Detect shapes outside of edge.
                            shape = self.layer.get_shape(self.x + col, edges[3] - step)

                            # Check if shape detected.
                            if shape != None:

                                # Add to list if so.
                                steps.append(shape)

                    # If detecting above.
                    elif direction == 4:

                        # Make sure at least one layer above.
                        if index + step + 1 < len(self.layer.level.layers):

                            # Loop through each row of shape.
                            for row in range(self.height):

                                # Keep track of shape's true y position.
                                y = self.layer.y + self.y + row

                                # Loop through each column of row.
                                for col in range(self.width):

                                    # Keep track of shape's true x position.
                                    x = self.layer.x + self.x + col

                                    # Detect shapes outside of edge.
                                    shape = self.layer.level.layers[index + step + 1].get_shape(x, y)

                                    # Check if shape detected.
                                    if shape != None:

                                        # Add to list if so.
                                        steps.append(shape)

                    # If detecting below.
                    elif direction == 5:

                        # Make sure at least one layer below.
                        if index - step - 1 >= 0:

                            # Loop through each row of shape.
                            for row in range(self.height):

                                # Keep track of shape's true y position.
                                y = self.layer.y + self.y + row

                                # Loop through each column of row.
                                for col in range(self.width):

                                    # Keep track of shape's true x position.
                                    x = self.layer.x + self.x + col

                                    # Detect shapes outside of edge.
                                    shape = self.layer.level.layers[index - step - 1].get_shape(x, y)

                                    # Check if shape detected.
                                    if shape != None:

                                        # Add to list if so.
                                        steps.append(shape)

                    # Append steps to shapes list.
                    shapes.append(steps)

                # Return shapes list.
                return shapes

            else:

                # Log invalid direction.
                log(f"Could not find nearby shapes of {self.__class__.__name__} {hex(id(self))} (not valid direction)", "error")

                # Return empty list.
                return []

        else:

            # Log negative or zero distance.
            log(f"Could not find nearby shapes of {self.__class__.__name__} {hex(id(self))} (negative or zero value)", "error")

            # Return empty list.
            return []


    def obstacles(self, distance, direction):
        """Detects if shape would collide with adjacent shapes if moved a
        specified distance in a specified direction."""

        # Check if distance is positive.
        if int(distance) > 0:

            # Check if direction is between 0 and 5.
            if int(direction) >= 0 and int(direction) < 6:

                # Makes sure shape is solid.
                if self.solid == True:

                    # Get nearby shapes.
                    shapes = self.nearby(int(distance), int(direction))

                    # Step through distance to find nearest obstacle.
                    for step in range(distance):

                        # Loop through shapes in each step.
                        for shape in shapes[step]:

                            # Make sure object is shape and solid.
                            if isinstance(shape, Shape) and shape.solid == True:

                                # Return shape if so.
                                return shape

                else:

                    # Log not solid. DISABLE due to log spam.
                    #log(f"Could not detect nearby obstacles of {self.__class__.__name__} {hex(id(self))} (not solid)", "error")

                    # Return none.
                    return None

            else:

                # Log invalid direction.
                log(f"Could not detect nearby obstacles of {self.__class__.__name__} {hex(id(self))} (not valid direction)", "error")

                # Return none.
                return None

        else:

            # Log negative or zero distance.
            log(f"Could not detect nearby obstacles of {self.__class__.__name__} {hex(id(self))} (negative or zero value)", "error")

            # Return none.
            return None


    def boundary(self, distance, direction):
        """Detects if a shape would collide with the edge of the layer if moved
        a specified distance in a specified direction."""

        # Check that distance is positive.
        if int(distance) > 0:

            # Check that direction is between 0 and 3.
            if int(direction) >= 0 and int(direction) < 4:

                # Makes sure layer has edges.
                if self.layer.edges == True:

                    # Calculate layer edges.
                    l = [self.layer.width, self.layer.height, 0, 0]

                    # Calculate shape edges.
                    s = [self.width + self.x + distance -1, self.height + self.y + distance -1,
                        self.x - distance, self.y - distance]

                    # Check if moving right/down or left/up.
                    if (((direction == 0 or direction == 1) and s[direction] >= l[direction])
                    or ((direction == 2 or direction == 3) and s[direction] < l[direction])):

                        # Return direction of boundary.
                        return str(direction)

                else:

                    # Log no edges. DISABLED due to log spam.
                    #log(f"Could not detect boundaries of {self.__class__.__name__} {hex(id(self))} (no edges)", "error")

                    # Return none.
                    return None

            else:

                # Log invalid direction.
                log(f"Could not detect boundaries of {self.__class__.__name__} {hex(id(self))} (not valid direction)", "error")

                # Return none.
                return None

        else:

            # Log negative or zero distance.
            log(f"Could not detect boundaries of {self.__class__.__name__} {hex(id(self))} (negative or zero value)", "error")

            # Return none.
            return None


    def set_position(self, x, y):
        """Changes the shape's position to the specified location in the layer."""

        # Update x and y values.
        self.x = int(x)
        self.y = int(y)

        # Log position change.
        log(f"Moved {self.__class__.__name__} {hex(id(self))} to ({x}, {y}) in {self.layer.__class__.__name__} {hex(id(self.layer))}")

        # Trigger on_move
        self.on_move()


    def move(self, x, y):
        """Moves the shape by the specified amount on the x and/or y axis."""

        # Set default responses.
        boundary = None
        obstacles = None

        # Check if moving right.
        if x > 0:

            # Detect edge and any obstacles.
            boundary = self.boundary(x, 0)
            obstacles = self.obstacles(x, 0)

        # Check if moving left.
        elif x < 0:

            # Detect edge and any obstacles.
            boundary = self.boundary(abs(x), 2)
            obstacles = self.obstacles(abs(x), 2)

        # Check if moving down.
        if y > 0:

            # Detect edge and any obstacles.
            boundary = self.boundary(y, 1)
            obstacles = self.obstacles(y, 1)

        # Check if moving up.
        elif y < 0:

            # Detect edge and any obstacles
            boundary = self.boundary(abs(y), 3)
            obstacles = self.obstacles(abs(y), 3)

        # Check for boundaries or obstacles.
        if boundary == None and obstacles == None:

            # Move shape if none.
            self.set_position(self.x + x, self.y + y)

            # Trigger on_move.
            self.on_move()

            # Return true.
            return True

        # Check if hit boundary.
        if boundary != None:

            # Trigger on_hit_edge if so.
            self.on_hit_edge(int(boundary))

        # Check if hit obstacle.
        if obstacles != None:

            # Trigger on_collide if so.
            self.on_collide(obstacles)

            # Trigger obstacle's on_collide.
            obstacles.on_collide()

        # Return false if no collision.
        return False


    def animate(self):
        """Moves the shape in its specified direction at its specified speed."""

        # Check if shape subscribed to on_tick.
        if not self.animate in self.layer.level.game.on_tick.subscribers:

            # Subscribe if not.
            self.layer.level.game.on_tick.subscribe(self.animate)

        # Check if frame counter matches speed.
        if int(self.frames) == self.speed:

            # Check if direction is right.
            if self.direction == 0:

                # Move to the right.
                self.move(1, 0)

            # Check if direction is right-down.
            elif self.direction == 1:

                # Move right-down.
                self.move(1, 1)

            # Check if direction is down.
            elif self.direction == 2:

                # Move down.
                self.move(0, 1)

            # Check if direction is down-left.
            elif self.direction == 3:

                # Move down-left.
                self.move(-1, 1)

            # Check if direction is left.
            elif self.direction == 4:

                # Move left.
                self.move(-1, 0)

            # Check if direction is left-up.
            elif self.direction == 5:

                # Move left-up.
                self.move(-1, -1)

            # Check if direction is up.
            elif self.direction == 6:

                # Move up.
                self.move(0, -1)

            # Check if direction is up-right.
            elif self.direction == 7:

                # Move up-right.
                self.move(1, -1)

            # Reset counter to 0.
            self.frames = 0

        else:

            # Iterate counter.
            self.frames += 1


    def freeze(self):
        """Stops the shape from animating but maintains direction and speed."""

        # Check if shape animation subscribed to on_tick.
        if self.animate in self.layer.level.game.on_tick.subscribers:

            # Unsubscribe if so.
            self.layer.level.game.on_tick.unsubscribe(self.animate)

            # Trigger on_freeze.
            self.on_freeze()

        else:

            # Log unsuccessful freeze.
            log(f"Could not freeze {self.__class__.__name__} {hex(id(self))} (not moving)", "error")


    def stop(self):
        """Stops the shape from moving and clears direction and speed."""

        # Check if shape animation subscribed to on_tick.
        if self.animate in self.layer.level.game.on_tick.subscribers:

            # Unsubscribe if so.
            self.layer.level.game.on_tick.unsubscribe(self.animate)

            # Clears direction and speed.
            self.direction = None
            self.speed = 0

            # Trigger on_stop.
            self.on_stop()

        else:

            # Log unsuccessful stop.
            log(f"Could not stop {self.__class__.__name__} {hex(id(self))} (not moving)", "error")


    def reverse(self):
        """Reverses the shape's current direction."""

        # Ensure shape is moving in a direction.
        if self.direction != None:

            # Check if direction is between 0 and 3.
            if self.direction >= 0 and self.direction <= 3:

                # Add 4 to reverse.
                self.direction += 4

                # Trigger on_reverse.
                self.on_reverse()

            # Check if direction is between 4 and 7.
            elif self.direction >= 4 and self.direction <= 7:

                # Minus 4 to reverse.
                self.direction -= 4

                # Trigger on_reverse.
                self.on_reverse()

        else:

            # Log unsuccessful reverse.
            log(f"Could not reverse the direction of {self.__class__.__name__} {hex(id(self))} (not moving)", "error")


def build_shape(width, height, character = " "):
    """Returns a two-dimensional list that represents the dimensions of a
    shape made out of a specified character."""

    # Check if width is positive.
    if int(width) > 0:

        # Check if height is positive.
        if int(height) > 0:

            # Check if character is single length.
            if len(str(character)) == 1:

                # Build shape list.
                shape = [[character for column in range(width)] for row in range(height)]

                # Return shape list.
                return shape

            else:

                # Log invalid character length.
                log(f"Could not build [{width}x{height}] shape with '{character}' (not valid length)", "error")

                # Return empty list.
                return []

        else:

            # Log negative or zero height.
            log(f"Could not build [{width}x{height}] shape with '{character}' (negative or zero height value)", "error")

            # Return empty list.
            return []

    else:

        # Log negative or zero width.
        log(f"Could not build [{width}x{height}] shape with '{character}' (negative or zero width value)", "error")

        # Return empty list.
        return []


def grid_to_string(grid):
    """Returns a string representation of specified grid."""

    # Check if list has at least one row.
    if len(grid) > 0:

        # Create string representation.
        string = '\n'.join([''.join(column) for column in grid])

        #Return the string.
        return string

    else:

        # Log invalid length.
        log(f"Could not convert '{grid}' to string (not valid length)", "error")

        # Return empty string.
        return ""


def log(message, tag = None):
    """Prints a message to the console log if enabled."""

    # Check if message contains at least one character.
    if len(str(message)) > 0:

        # Print tagged logs.
        if ("-debug" in sys.argv or "-log" in sys.argv) and tag != None and tag != "":

            # Get line number.
            linenum = inspect.getouterframes(inspect.currentframe())[-1:][0][2]

            # Format message.
            message = f"[{tag.upper()}: Line {linenum}] {message}"

            # Print to log.
            print(f"plumpton: {message}")

        # Print other logs if enabled in command line.
        elif "-log" in sys.argv and (tag == None or tag == ""):

            # Print to log.
            print(f"plumpton: {message}")

    else:

        # Get line number.
        linenum = inspect.getouterframes(inspect.currentframe())[-1:][0][2]

        # Print logging error.
        print(f"plumpton: [ERROR: Line {linenum}] Logging error.")


if __name__ == "__main__":
    print(f"plumpton version {PLUMPTON_VERSION}")
    print("Copyright (C) 2018 Thomas Woodcock <https://thomaswoodcock.net>")
