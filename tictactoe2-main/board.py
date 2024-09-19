import pygame
import math

SIZE = 250
LINE_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)
CROSS_COLOR = (255, 0, 0)
CIRCLE_COLOR = (0, 0, 255)
border = 14

class Square:
    def __init__(self):
        self.value = 0 # 0 for empty, 1 for X, 2 for O
        self.x = 0
        self.y = 0

class Board():
    def __init__(self, screen, size) -> None:
        self.squares = [[Square() for i in range(3)] for i in range(3)] #tictactoe game with 2d array -> grid
        self.screen = screen
        self.turn = 0
        self.size = size
        self.value = 0
        self.x = 0
        self.y = 0
        self.last_move = (0,0)
        self.border = border

    def init_squares(self, x, y, screen_width) -> None: # Initialize the squares
        border = round((screen_width-3*self.size)/4)
        for row in range(len(self.squares)): # iterate over each row
            for col in range(3): # iterate over each square in the row
                self.squares[row][col].x = (col + 1)* border + (col * self.size) + x
                self.squares[row][col].y = (row + 1) * border + (row * self.size) + y

    def render(self) -> None: # Render the board
        x, y = self.x + self.size/2, self.y + self.size/2
        length, extend = self.size*4, 10

        # Draw the lines for the board
        self.draw_line(x - extend, y + self.size*1.25, x+length+extend, y + self.size*1.25)
        self.draw_line(x + self.size*1.25, y - extend, x + self.size*1.25, y + length+extend)
        self.draw_line(x - extend, y + self.size*2.75, x+length+extend, y + self.size*2.75)
        self.draw_line(x + self.size*2.75, y - extend, x + self.size*2.75, y + length+extend)

        # Draw the squares
        for row in self.squares:
            for sq in row:
                if sq.value == 1:
                    self.draw_cross(sq.x, sq.y)
                elif sq.value == 2:
                    self.draw_circle(sq.x, sq.y)

    def draw_line(self, start_x, start_y, end_x, end_y): # Draw a line from start to end
        pygame.draw.line(self.screen, LINE_COLOR, (start_x, start_y), (end_x, end_y), 2)

    def draw_cross(self, x, y): # Draw a cross in the square
        length = math.sqrt(self.size*self.size)-self.size/20
        top_left = (x + self.size / 20, y + self.size / 20)
        bottom_right = (x + length, y + length)
        bottom_left = (x+ self.size / 20, y + length)
        top_right = (x + length, y + self.size / 20)
        pygame.draw.line(self.screen, CROSS_COLOR, start_pos=top_left, end_pos=bottom_right, width=2)
        pygame.draw.line(self.screen, CROSS_COLOR, start_pos=bottom_left, end_pos=top_right, width=2)

    def draw_circle(self, x, y): # Draw a circle in the square
        center = (x+(self.size/2), y+(self.size/2))
        pygame.draw.circle(self.screen, CIRCLE_COLOR, center, self.size/2 - 3, width=2)

    def check_square(self, x, y, turn) -> bool: # Return True if the move is valid, False otherwise! Also updates the board if valid.
        if(self.value):
            return
        for row in range(3):
            for col in range(3):
                sq = self.squares[row][col]
                if x in range(sq.x, sq.x + self.size) and y in range(sq.y, sq.y + self.size) and sq.value == 0:
                    sq.value = 1 if turn else 2
                    self.last_move = (row, col)
                    return True
        return False

    def check_board_state(self) -> int: # -1 for nothing, 0 for draw, 1 for winner
        self.turn = self.turn+1
        values = []
        for row in self.squares:
            values.append([x.value for x in row])

        for i in range(3):
            if(values[i][0] == values[i][1] == values[i][2] != 0): 
                return 1
            if(values[0][i] == values[1][i] == values[2][i] != 0): 
                return 1
        if(values[0][0] == values[1][1] == values[2][2] != 0 or values[0][2] == values[1][1] == values[2][0] != 0):
            return 1
        
        if(self.turn == 9):
            return 0

        return -1

class BigBoard():
    def __init__(self, screen):
        self.initialize_boards(screen)
        self.screen = screen
        self.value = 0
        self.turn = 0
        self.last_move = (-1, -1)
        self.valid_boards = [(i, j) for i in range(3) for j in range(3)]

    def initialize_boards(self, screen):
        self.boards = [[self.create_board(screen, 50) for _ in range(3)] for _ in range(3)]
        self.set_board_positions(screen.get_width())

    def create_board(self, screen, size):
        return Board(screen, size)

    def set_board_positions(self, width):
        border = round((width - 3 * SIZE) / 4)
        for row in range(len(self.boards)):
            for col in range(3):
                self.set_board_position(row, col, border)

    def set_board_position(self, row, col, border):
        board = self.boards[row][col]
        board.x = (col + 1) * border + (col * SIZE)
        board.y = (row + 1) * border + (row * SIZE)
        board.init_squares(board.x, board.y, SIZE)
        board.border = border

    def render(self):
        self.screen.fill(BG_COLOR)
        for row in self.boards:
            for board in row:
                self.render_board(board)
        self.highlight_last_move()

    def render_board(self, board):
        board.render()
        if board.value > 0:
            self.render_winner_overlay(board)

    def render_winner_overlay(self, board):
        surface = self.create_transparent_surface(SIZE, SIZE)
        self.screen.blit(surface, (board.x, board.y))
        self.draw_winner_symbol(board)

    def create_transparent_surface(self, width, height):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((*BG_COLOR, 200))
        return surface

    def draw_winner_symbol(self, board):
        REDUCTION_FACTOR = 0.8
        if board.value == 1:
            self.draw_x(board, REDUCTION_FACTOR)
        elif board.value == 2:
            self.draw_o(board, REDUCTION_FACTOR)

    def draw_x(self, board, reduction_factor):
        start_pos1 = (board.x + SIZE * (1 - reduction_factor) / 2, board.y + SIZE * (1 - reduction_factor) / 2)
        end_pos1 = (board.x + SIZE * (1 + reduction_factor) / 2, board.y + SIZE * (1 + reduction_factor) / 2)
        start_pos2 = (board.x + SIZE * (1 - reduction_factor) / 2, board.y + SIZE * (1 + reduction_factor) / 2)
        end_pos2 = (board.x + SIZE * (1 + reduction_factor) / 2, board.y + SIZE * (1 - reduction_factor) / 2)
        pygame.draw.line(self.screen, CROSS_COLOR, start_pos=start_pos1, end_pos=end_pos1, width=3)
        pygame.draw.line(self.screen, CROSS_COLOR, start_pos=start_pos2, end_pos=end_pos2, width=3)

    def draw_o(self, board, reduction_factor):
        center = (board.x + SIZE / 2, board.y + SIZE / 2)
        radius = SIZE / 2 * reduction_factor - 3
        pygame.draw.circle(self.screen, CIRCLE_COLOR, center, radius, width=3)

    def highlight_last_move(self):
        if self.last_move != (-1, -1):
            i, j = self.last_move
            next_board = self.boards[i][j]
            if next_board.value == 0:  # If the next board is not won or full
                self.highlight_board(i, j)
                self.valid_boards = [(i, j)]
            else:  # If the next board is won or full, highlight all legal boards
                for row in range(3):
                    for col in range(3):
                        if self.boards[row][col].value == 0:
                            self.highlight_board(row, col)
                            valid_boards = []
                            valid_boards.append((row, col))
                            self.valid_boards = valid_boards

    def highlight_board(self, row, col):
        board = self.boards[row][col]
        border_rect = pygame.Rect(board.x - border, board.y - border, SIZE + 2 * border, SIZE + 2 * border)
        pygame.draw.rect(self.screen, LINE_COLOR, border_rect, width=3)

    def check_square(self, x, y, turn) -> tuple: 
        # Iterate over each square in the 3x3 board
        for row in range(3):
            for col in range(3):
                sq = self.boards[row][col]
                # Check if the coordinates are within the square's boundaries and the square is not filled
                if sq.x <= x < sq.x + SIZE and sq.y <= y < sq.y + SIZE and sq.value == 0:
                    # Check if the move is valid according to Super Tic Tac Toe rules
                    if (row, col) == self.last_move or self.boards[self.last_move[0]][self.last_move[1]].value > 0 or self.last_move == (-1, -1):
                        # If the move is valid, update last_move and return the square's position
                        if sq.check_square(x, y, turn):
                            self.last_move = sq.last_move
                            return (row, col)

        # If no valid move is found, return (-1, -1)
        return (-1, -1)

    def check_board_state(self, val, turn):
        """Check the state of the game board, see if there's a winner.
           Returns 1 if player 1 wins, 2 if player 2 wins, 0 if it's a draw,
           and -1 if the game is still ongoing."""
        board = self.boards[val[0]][val[1]]
        state = board.check_board_state()

        if state > 0:
            self.boards[val[0]][val[1]].value = 1 if turn else 2

        # Check for a winner
        for i in range(3):
            if self.check_row(i) or self.check_column(i):
                return 1 if turn else 2

        # Check diagonals
        if self.check_diagonal():
            return 1 if turn else 2

        return -1  # No winner yet
    
    def check_row(self, row):
        """Check if all values in a row are the same and not 0."""
        return self.boards[row][0].value == self.boards[row][1].value == self.boards[row][2].value != 0

    def check_column(self, column):
        """Check if all values in a column are the same and not 0."""
        return self.boards[0][column].value == self.boards[1][column].value == self.boards[2][column].value != 0

    def check_diagonal(self):
        """Check if all values in both diagonals are the same and not 0."""
        diagonal1 = self.boards[0][0].value == self.boards[1][1].value == self.boards[2][2].value != 0
        diagonal2 = self.boards[0][2].value == self.boards[1][1].value == self.boards[2][0].value != 0
        return diagonal1 or diagonal2