import time
from app.models.generator import generate_unique_board
from app.models.conquest_generator import generate_conquest_board

class GameController:
    def __init__(self, board_size, gen_mode="random"):
        self.board_size = board_size
        self.gen_mode   = gen_mode  # "random" o "conquest"
        self.start_game()

    def start_game(self):
        """
        Initialize a new game using selected generation mode:
        - "random": generate_unique_board
        - "conquest": generate_conquest_board
        Then reset user and error boards and timer.
        """
        if self.gen_mode == "conquest":
            sol, col = generate_conquest_board(self.board_size)
        else:
            sol, col = generate_unique_board(self.board_size)

        self.solution_queen_board = sol
        self.colored_board        = col

        n = self.board_size
        self.user_board  = [['' for _ in range(n)] for __ in range(n)]
        self.error_board = [[False for _ in range(n)] for __ in range(n)]
        self.start_time  = time.time()

    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        m, s = divmod(int(elapsed), 60)
        return f"{m:02d}:{s:02d}"

    def scan_errors(self):
        n = self.board_size
        self.error_board = [[False]*n for _ in range(n)]
        queens_pos = [
            (r, c)
            for r in range(n)
            for c in range(n)
            if self.user_board[r][c] == 'Q'
        ]
        def mark(a, b):
            (r1, c1), (r2, c2) = a, b
            self.error_board[r1][c1] = True
            self.error_board[r2][c2] = True

        for i in range(len(queens_pos)):
            for j in range(i+1, len(queens_pos)):
                r1, c1 = queens_pos[i]
                r2, c2 = queens_pos[j]
                # adjacent
                if max(abs(r1-r2), abs(c1-c2)) == 1:
                    mark((r1, c1), (r2, c2))
                # same row/col
                if r1 == r2 or c1 == c2:
                    mark((r1, c1), (r2, c2))
                # same color region
                if self.colored_board[r1][c1] == self.colored_board[r2][c2]:
                    mark((r1, c1), (r2, c2))

    def update_move(self, row, col, move_type):
        current = self.user_board[row][col]
        if move_type == "cross":
            new = 'X'
        elif move_type == "queen":
            new = 'Q'
        elif move_type == "clear":
            new = ''
        else:
            new = current

        self.user_board[row][col] = new
        message = ""
        if new == 'Q':
            correct = self.solution_queen_board[row]
            if col != correct:
                message = "Incorrect queen position."

        self.scan_errors()
        return True, message

    def is_game_complete(self):
        for r, correct_col in enumerate(self.solution_queen_board):
            if self.user_board[r][correct_col] != 'Q':
                return False
        for row in self.error_board:
            if any(row):
                return False
        return True

    def get_game_state(self):
        return {
            "user_board":    self.user_board,
            "error_board":   self.error_board,
            "colored_board": self.colored_board,
            "elapsed_time":  self.get_elapsed_time(),
            "is_complete":   self.is_game_complete(),
            "gen_mode":      self.gen_mode
        }

    def reset_game(self, board_size, gen_mode=None):
        if gen_mode:
            self.gen_mode = gen_mode
        self.board_size = board_size
        self.start_game()
