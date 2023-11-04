import pygame
import mido
import threading
import json

from notes import NOTE_NAME_MAPPING

class ColorGridApp:
    def __init__(self):
        # Set the grid size
        self.GRID_SIZE = (12, 8)

        # Configure keys that will refresh the grid
        self.REFRESH_KEYS = set([pygame.K_RETURN])

        # Initialize pygame and MIDI output
        pygame.init()

        # Create the array
        self._construct_grid()
        self._construct_grid_states()

        self._load_note_colors()
        self._map_notes()


        # Set default state to running
        self.running = True

        # Create array to store pressed keys
        self.pressed_keys = set()

    def _construct_grid_states(self):
        # Set of states that correspond to whether the square is lit up
        self.square_states = [
            [(False, (0, 0, 0)) for _ in range(self.GRID_HEIGHT)] for _ in range(self.GRID_WIDTH)
        ]

    def _construct_grid(self):
        # Create a grid with squares
        self.GRID_WIDTH, self.GRID_HEIGHT = self.GRID_SIZE
        self.SQUARE_SIZE = 50
        self.screen = pygame.display.set_mode(
            (self.GRID_WIDTH * self.SQUARE_SIZE, self.GRID_HEIGHT * self.SQUARE_SIZE)
        )
        self.squares = [
            [
                pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                for _ in range(self.GRID_HEIGHT)
            ]
            for _ in range(self.GRID_WIDTH)
        ]

    def _load_note_colors(self):
        with open('note_colors.json', 'r') as json_file:
            self.NOTE_COLOR_MAPPING = json.load(json_file)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _calculate_note_index(self, note):
        index = 120 - note

        return max(min(index, 96), 0)
    
    def _calculate_note_from_index(self, index):
        note = 120 - index
        return max(min(note, 120), 24)

    def _map_note_to_square(self, note):
        # Map MIDI note to a square in the grid
        note_name = NOTE_NAME_MAPPING[note]
        note_index = self._calculate_note_index(note)
        note_color_hex = self.NOTE_COLOR_MAPPING[note_name]
        note_color_rgb = self._hex_to_rgb(note_color_hex)
        return (note_index % self.GRID_WIDTH, note_index // self.GRID_WIDTH, note_color_rgb)

    def _map_notes(self):
        for index in range(96):
            note = self._calculate_note_from_index(index)
            square_x, square_y, color = self._map_note_to_square(note)
            self.square_states[square_x][square_y] = (True, color)

    def _render(self):
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                isOn = self.square_states[x][y][0]
                color = self.square_states[x][y][1]
                if isOn:
                    self.squares[x][y].fill(color) # Fill with note color
                else:
                    self.squares[x][y].fill((0, 0, 0))  # Fill square with black

                self.screen.blit(
                    self.squares[x][y], (x * self.SQUARE_SIZE, y * self.SQUARE_SIZE)
                )

        pygame.display.flip()

    def start(self):
        self._render()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in self.REFRESH_KEYS:
                        self._load_note_colors()
                        self._map_notes()
                        self._render()

                elif event.type == pygame.KEYUP:
                    if event.key in self.pressed_keys:
                        self.pressed_keys.remove(event.key)



        pygame.quit()
        quit()


if __name__ == "__main__":
    app = ColorGridApp()
    app.start()