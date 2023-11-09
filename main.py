import pygame
import mido
import threading
import json

from notes import NOTE_NAME_MAPPING


class WavPlayer:
    def __init__(self):
        pygame.mixer.init()

    def start_wav(self, wav_file_path):
        sound = pygame.mixer.Sound(wav_file_path)
        sound.play()

    def stop(self):
        pygame.mixer.stop()


class MidiPlayer:
    def __init__(self, grid_size):
        self.GRID_SIZE = grid_size
        self.GRID_WIDTH, self.GRID_HEIGHT = self.GRID_SIZE
        self.BASE_MIDI_NOTE = 24
        self.MAX_INDEX = self.GRID_WIDTH * self.GRID_HEIGHT

        # Set of states that correspond to whether the square is lit up
        self.square_states = [
            [(False, (0, 0, 0), 127) for _ in range(self.GRID_HEIGHT)]
            for _ in range(self.GRID_WIDTH)
        ]

        # A lock ensures that nothing else can edit the variable while we're changing it
        self.lock = threading.Lock()

        self._load_note_colors()

    def _load_note_colors(self):
        with open("note_colors.json", "r") as json_file:
            self.NOTE_COLOR_MAPPING = json.load(json_file)

    def _set_square_state(self, square_x, square_y, state, color, velocity):
        with self.lock:
            self.square_states[square_x][square_y] = (state, color, velocity)

    def _calculate_note_index(self, note):
        adjusted_note = self.MAX_INDEX - (note - self.BASE_MIDI_NOTE)

        return max(min(adjusted_note, self.MAX_INDEX), 0)

    def _hex_to_rgb(self, hex_color):
        # source from here: https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _map_note_to_square(self, note):
        # Map MIDI note to a square in the grid
        note_name = NOTE_NAME_MAPPING[note]
        note_index = self._calculate_note_index(note)
        note_color_hex = self.NOTE_COLOR_MAPPING[note_name]
        note_color_rgb = self._hex_to_rgb(note_color_hex)
        return (
            note_index % self.GRID_WIDTH,
            note_index // self.GRID_WIDTH,
            note_color_rgb,
        )

    def _play_midi(self, midi_file_path):
        midi_file = mido.MidiFile(midi_file_path)

        for msg in midi_file.play():
            if msg.type == "note_on":
                square_x, square_y, color = self._map_note_to_square(msg.note)
                self._set_square_state(square_x, square_y, True, color, msg.velocity)
            elif msg.type == "note_off":
                square_x, square_y, color = self._map_note_to_square(msg.note)
                self._set_square_state(square_x, square_y, False, color, msg.velocity)

        print(f"{midi_file_path} file ended")

    def start_midi(self, midi_file_path):
        # We call daemon=True so that the thread dies when main dies
        midi_thread = threading.Thread(
            target=self._play_midi, args=(midi_file_path,), daemon=True
        )

        midi_thread.start()


class MIDIRainbow:
    # the __init__ function initialises an instance of this class
    # if you replace the word self with me/my it'll make sense. example self.grid size = my. grid size is 12 by 8
    def __init__(self):
        # Set the grid size variable (variables allow you to give a name to data that you can use to reference later to access it)
        self.GRID_SIZE = (12, 6)

        # Define MIDI and WAV file paths for each key
        # pygame is defining what a key on the keyboard is and we are mapping information to each key
        self.MEDIA_FILES = {
            pygame.K_a: ("midi/piano_1.mid", "wav/piano_1.wav"),
            pygame.K_s: ("midi/piano_2.mid", "wav/piano_2.wav"),
            pygame.K_d: ("midi/piano_3.mid", "wav/piano_3.wav"),
            pygame.K_f: ("midi/piano_4.mid", "wav/piano_4.wav"),
            pygame.K_g: ("midi/piano_5.mid", "wav/piano_5.wav"),
            pygame.K_h: ("midi/piano_6.mid", "wav/piano_6.wav"),
            pygame.K_j: ("midi/drums_1.mid", "wav/drums_1.wav"),
            pygame.K_k: ("midi/drums_2.mid", "wav/drums_2.wav"),
            pygame.K_l: ("midi/drums_3.mid", "wav/drums_3.wav"),
            pygame.K_SEMICOLON: ("midi/drums_4.mid", "wav/drums_4.wav"),
            pygame.K_QUOTE: ("midi/drums_5.mid", "wav/drums_5.wav"),
            pygame.K_RETURN: ("midi/drums_6.mid", "wav/drums_6.wav"),
            pygame.K_SPACE: ("midi/chords.mid", "wav/chords.wav"),
        }

        # Initialize pygame
        # pygame is a library that provides utility for creating visual desktop applications
        pygame.init()

        # Set the name of the window
        pygame.display.set_caption("MIDI Rainbow")

        # Create the array
        self._construct_grid()

        # Set default state to running
        self.running = True

        # Create the midi player class
        self.midi_player = MidiPlayer(grid_size=self.GRID_SIZE)

        self.wav_player = WavPlayer()

        # Create array to store pressed keys
        self.pressed_keys = set()

    def _construct_grid(self):
        # Create a grid with squares
        self.GRID_WIDTH = self.GRID_SIZE[0]
        self.GRID_HEIGHT = self.GRID_SIZE[1]
        self.SQUARE_SIZE = 50  # square size in pixel

        screen_pixel_width = self.GRID_WIDTH * self.SQUARE_SIZE
        screen_pixel_height = self.GRID_HEIGHT * self.SQUARE_SIZE

        self.screen = pygame.display.set_mode((screen_pixel_width, screen_pixel_height))

        # the squares variable is a two dimensional array that stores the color information
        # of a grid using an instance of the pygame.Surface class (aka an object)
        # self.squares = []
        # for column in range(self.GRID_WIDTH):
        #     rows = []
        #     for row in range(self.GRID_HEIGHT):
        #         grid_surface = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
        #         rows.append(grid_surface)

        #     self.squares.append(row)
        # Create a grid with squares
        self.squares = [
            [
                pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                for _ in range(self.GRID_HEIGHT)
            ]
            for _ in range(self.GRID_WIDTH)
        ]

    def _velocity_to_opacity(self, velocity):
        max_velocity = 127
        max_opacity = 255
        opacity = (velocity / max_velocity) * max_opacity
        return round(opacity)

    def _render(self):
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                with self.midi_player.lock:
                    isOn = self.midi_player.square_states[x][y][0]
                    color = self.midi_player.square_states[x][y][1]
                    velocity = self.midi_player.square_states[x][y][2]
                    opacity = self._velocity_to_opacity(velocity)
                    if isOn:
                        self.squares[x][y].fill(color)  # Fill with note color
                        self.squares[x][y].set_alpha(opacity)
                    else:
                        self.squares[x][y].fill((0, 0, 0))  # Fill square with black
                        self.squares[x][y].set_alpha(255)

                    self.screen.blit(
                        self.squares[x][y], (x * self.SQUARE_SIZE, y * self.SQUARE_SIZE)
                    )

        pygame.display.flip()

    def start(self):
        pygame.display.update()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in self.MEDIA_FILES:
                        # Make sure we don't trigger multiple plays if key is held
                        self.pressed_keys.add(event.key)
                        midi_file_path, wav_file_path = self.MEDIA_FILES[event.key]
                        if midi_file_path:
                            self.midi_player.start_midi(midi_file_path)

                        if wav_file_path:
                            self.wav_player.start_wav(wav_file_path)

                elif event.type == pygame.KEYUP:
                    if event.key in self.pressed_keys:
                        self.pressed_keys.remove(event.key)

            self._render()

        pygame.quit()
        quit()


# this is where the program starts
if __name__ == "__main__":
    # create an instance of MIDIRainbow called app
    # this will call the __init__ function of the class
    app = MIDIRainbow()
    app.start()
