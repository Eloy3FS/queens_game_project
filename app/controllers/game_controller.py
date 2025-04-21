# app/controllers/game_controller.py

import time
from app.models import queens, coloring

class GameController:
    def __init__(self, board_size):
        self.board_size = board_size
        self.start_game()
        
    def start_game(self):
        # 1) solution & colored
        self.solution_queen_board = queens.generate_random_board(self.board_size)
        self.colored_board, _     = coloring.color_board(
            self.solution_queen_board, self.board_size
        )
        # 2) user board: '' / 'X' / 'Q'
        n = self.board_size
        self.user_board  = [['' for _ in range(n)] for __ in range(n)]
        self.error_board = [[False for _ in range(n)] for __ in range(n)]
        # 3) timer
        self.start_time = time.time()

    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        m, s = divmod(int(elapsed), 60)
        return f"{m:02d}:{s:02d}"

    def scan_errors(self):
        """
        Recompute error_board by flagging every pair of queens
        that conflict by:
         - distance‑1 (orthogonal or diagonal)
         - same row or column
         - same colored_cell in colored_board
        """
        n = self.board_size
        self.error_board = [[False]*n for _ in range(n)]
        # collect queen positions
        queens_pos = [
            (r,c)
            for r in range(n) for c in range(n)
            if self.user_board[r][c] == 'Q'
        ]
        def mark(a,b):
            (r1,c1),(r2,c2) = a,b
            self.error_board[r1][c1] = True
            self.error_board[r2][c2] = True

        for i in range(len(queens_pos)):
            for j in range(i+1, len(queens_pos)):
                r1,c1 = queens_pos[i]
                r2,c2 = queens_pos[j]
                # distance‑1
                if max(abs(r1-r2), abs(c1-c2)) == 1:
                    mark((r1,c1),(r2,c2))
                # same row/col
                if r1==r2 or c1==c2:
                    mark((r1,c1),(r2,c2))
                # same solution color
                if self.colored_board[r1][c1] == self.colored_board[r2][c2]:
                    mark((r1,c1),(r2,c2))

    def update_move(self, row, col, move_type):
        """
        1) cycle cell state:
           '' -> 'X' -> 'Q' -> ''
        2) after any change, re‑scan all errors
        Returns (always valid=True, optional message)
        """
        current = self.user_board[row][col]
        # determine new state
        if move_type == "cross":
            new = 'X'
        elif move_type == "queen":
            new = 'Q'
        elif move_type == "clear":
            new = ''
        else:
            new = current

        self.user_board[row][col] = new

        # optional hint only when placing a queen
        message = ""
        if new == 'Q':
            # check if that placement is the correct column
            correct = self.solution_queen_board[row]
            if col != correct:
                message = "Incorrect queen position."

        # recompute all errors
        self.scan_errors()

        return True, message

    def is_game_complete(self):
        """
        True if every row has a queen in the correct column
        and there are no errors flagged.
        """
        # all rows correct?
        for r,correct_col in enumerate(self.solution_queen_board):
            if self.user_board[r][correct_col] != 'Q':
                return False
        # no errors?
        for row in self.error_board:
            if any(row):
                return False
        return True

    def get_game_state(self):
        return {
            "user_board":      self.user_board,
            "error_board":     self.error_board,
            "colored_board":   self.colored_board,
            "elapsed_time":    self.get_elapsed_time(),
            "is_complete":     self.is_game_complete()
        }

    def reset_game(self, board_size):
        self.board_size = board_size
        self.start_game()
