import pygame
from board import BigBoard
import os
import sys
import random
import request_handler

INVALID_SQUARE = (-1, -1)

class Game: 
    def __init__(self, screen, localPlayer, local=False, ai=False) -> None:
        self.localPlayer = localPlayer  # 'X' or 'O', representing the local player
        self.currentTurn = 'X'  # 'X' or 'O', representing whose turn it is
        self.active = True  # Whether the game is currently active
        self.board = BigBoard(screen)  # The game board
        self.font = pygame.font.SysFont('hightowertext', 90)  # Font for displaying text
        self.screen = screen  # The game screen
        self.last_move = INVALID_SQUARE  # The last move made
        self.local = local
        self.ai = ai

    def render(self): 
        """Renders the game on the screen."""

        if self.active:
            self.board.render()
            text_message = self.get_turn_message()
            text = self.font.render(text_message, True, 0)
            text_rect = text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()-50))
            self.screen.blit(text, text_rect)
            pygame.display.update()
            if(self.ai and self.currentTurn == 'O'):
                pygame.time.wait(random.randint(500, 2000))
                self.ai_move()

    def get_turn_message(self):
        """Returns a message indicating whose turn it is."""
        if self.local:
            return "%s's turn" % self.currentTurn
        elif self.currentTurn == self.localPlayer:
            return "Your turn!"
        else:
            return "Opponent's turn!"

    def handle_click(self, x, y, force=False): 
        if not force and (not self.active or self.localPlayer != self.currentTurn):
            if(not self.local or self.ai and self.currentTurn == 'O'):
                return False
        
        clicked_square = self.board.check_square(x, y, self.currentTurn == 'X')
        if clicked_square != INVALID_SQUARE:
            state = self.board.check_board_state(clicked_square, self.currentTurn == 'X')
            self.last_move = clicked_square
            if state >= 0:
                self.end_game(state)
            self.currentTurn = 'O' if self.currentTurn == 'X' else 'X'
            self.last_move = (x, y)
            return True

    def ai_move(self):
        valid_moves = self.get_valid_moves()
        random_move = random.choice(valid_moves)
        self.handle_click(random_move[0], random_move[1], force=True)

    def get_valid_moves(self):
        valid_moves = []
        for i in range(len(self.board.boards)):
            for j in range(len(self.board.boards[i])):
                board = self.board.boards[i][j]
                if (i, j) in self.board.valid_boards:
                    for square_row in board.squares:
                        for square in square_row:
                            if square.value == 0:
                                valid_moves.append((square.x, square.y))
        return valid_moves

    def get_state(self):
        state = []
        for i in range(len(self.board.boards)):
            for j in range(len(self.board.boards[i])):
                board = self.board.boards[i][j]
                for square_row in board.squares:
                    for square in square_row:
                        state.append(square.value)
        return state

    def end_game(self, state):
        self.active = False
        self.screen.fill((255, 255, 255))
        # STATE IS 0 IF DRAW, 1 IF X WON, 2 IF O WON.
        if not self.local:
            if state == 0:
                raise NotImplementedError("DRAW")
            elif state == 1 and self.localPlayer == 'X':
                request_handler.win_game()
            elif state == 2 and self.localPlayer == 'O':
                request_handler.win_game()
            else:
                request_handler.lose_game()

        text_str = "{} WON THE GAME" if state > 0 else "DRAW!"
        text = self.font.render(text_str.format(self.currentTurn), True, 0)
        text_rect = text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/2))
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(5000)
        os.execl(sys.executable, sys.executable, *sys.argv)
