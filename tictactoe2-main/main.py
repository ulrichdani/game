import pygame
from game import Game
from websocket import create_connection
from menu import Menu
import threading
import sys, os
import request_handler

pygame.init()
pygame.font.init()

# Define screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 1000

# Define game states
MENU = 0
GAME = 1

class Main:
    _instance = None
    username = ""

    # return singleton instance!
    @staticmethod
    def get_instance():
        if Main._instance is None:
            Main._instance = Main()
        return Main._instance

    def __init__(self) -> None:
        # Set initial game state to MENU
        self.state = MENU
        self.ws = None
        self.token = None
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.menu = Menu.get_instance(self.screen, self)
        self.player = ''
        pygame.display.set_caption("MY PROJECT")
        pygame.display.update()
        self.game = None
        self.local = False
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                self.token = f.read()
            r = request_handler.get_username(self.token)
            if r == None:
                os.remove("token.txt")
                self.token = None
            else:
                Main.username = r
        request_handler.preset_token = self.token
        Menu.first_update()

    def loop(self):
        # Main game loop
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.render_states()
            pygame.display.update()
            clock.tick(20)

    def handle_events(self):
        # Handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN: #check for mouse click and pos
                x, y = e.pos
                self.click(x, y)
            elif e.type == pygame.KEYDOWN:
                if self.state == MENU:
                    self.menu.handle_keydown(e)

    def render_states(self):
        # Render menus and game states
        if self.state == MENU:
            self.menu.render()
        elif self.state == GAME:
            self.game.render()

    
    def click(self, x, y):
        # Handle click events based on game state
        if self.state == MENU:
            self.menu.click(x, y)
        elif self.state == GAME:
            if self.game.handle_click(x, y):
                pygame.display.update()
                if not self.local:
                    self.ws.send_text(str(self.game.last_move))

    def open_websocket(self):
        # Open websocket in a new thread
        self.ws_thread = threading.Thread(target=self.start_websocket, daemon=True)
        self.ws_thread.start()

    def close_websocket(self):
        # Close websocket
        self.ws.close()
        self.ws = None
        self.state = MENU
        self.game = None
        self.player = ''

    def start_websocket(self):
        # Start websocket connection
        if not os.path.exists("token.txt"):
            raise Exception("NOT LOGGED IN YET!")
        self.ws = create_connection("ws://164.92.255.66:8000/ws")
        self.ws.send(self.token)
        while self.ws:
            message = self.ws.recv()
            if message[:7] == "WELCOME":
                continue
            if message == "disconnected":
                self.opponent_disconnect()
            elif self.state == MENU:
                self.handle_menu_state(message)
            elif self.state == GAME:
                self.handle_game_state(message)

    def handle_menu_state(self, message):
        if message == "1":
            self.player = 'X'
        elif message == "2":
            self.start_game()

    def start_game(self):
        if self.player == '':
            self.player = 'O'
        self.game = Game(self.screen, self.player)
        self.state = GAME

    def start_local_game(self):
        self.game = Game(self.screen, 'X', local=1, ai=False)
        self.state = GAME
        self.local = True
        
    def start_local_game_vs_ai(self):
        self.game = Game(self.screen, 'X', local=1, ai=True)
        self.state = GAME
        self.local = True

    def handle_game_state(self, message):
        x, y = message.replace("(", "").replace(")", "").split(", ")
        self.game.handle_click(int(x), int(y), force=True)

    def opponent_disconnect(self):
        self.ws.close()
        self.ws = None
        self.state = MENU
        self.game = None
        self.player = ''
        request_handler.win_game()

if __name__ == '__main__':
    main = Main.get_instance()
    main.loop()
