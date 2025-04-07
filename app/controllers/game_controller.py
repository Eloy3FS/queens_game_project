import time
from models import queens, coloring

class GameController:
    def __init__(self, board_size):
        self.board_size = board_size
        self.start_game()
        
    def start_game(self):
        # Generate the solution queen board (list of column indices per row)
        self.solution_queen_board = queens.generate_random_board(self.board_size)
        # Generate the colored board and the solution number board
        self.colored_board, self.solution_number_board = coloring.color_board(self.solution_queen_board, self.board_size)
        # Initialize the user board: start with all cells set to "X" (cross)
        self.user_board = [['X' for _ in range(self.board_size)] for _ in range(self.board_size)]
        # Error board: a boolean matrix that marks cells with an error (False = no error)
        self.error_board = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        # Record the game start time (for the timer)
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def validate_move(self, row, col, move_type):
        """
        Validate a move for the cell at (row, col) given the move_type.
        For a "queen" move:
          - The queen must be placed in the correct cell (as determined by the solution).
          - There must be no other queen in the same row or column.
        For a "cross" move, no additional validation is needed.
        
        Returns:
            tuple: (valid: bool, message: str)
        """
        message = ""
        valid = True
        
        if move_type == "queen":
            # Check if the cell already contains a queen
            if self.user_board[row][col] == 'Q':
                valid = False
                message = "A queen is already placed here."
            else:
                # Validate that the queen is in the correct position
                correct_col = self.solution_queen_board[row]
                if col != correct_col:
                    valid = False
                    message = "Incorrect queen position."
                # Check for a duplicate queen in the same column in another row
                for r in range(self.board_size):
                    if r != row and self.user_board[r][col] == 'Q':
                        valid = False
                        message = "Another queen is already placed in this column."
                        break
        elif move_type == "cross":
            # For a cross move, accept it without error checking.
            valid = True
        else:
            valid = False
            message = "Invalid move type."
        
        return valid, message
    
    def update_move(self, row, col, move_type):
        """
        Update the game state when a move is made.
        If the move is valid, update the user board.
        If invalid, mark that cell in the error board.
        
        Args:
            row (int): The row index of the move.
            col (int): The column index of the move.
            move_type (str): The type of move ("queen" or "cross").
        
        Returns:
            tuple: (valid: bool, message: str)
        """
        valid, message = self.validate_move(row, col, move_type)
        if valid:
            if move_type == "queen":
                self.user_board[row][col] = 'Q'
                self.error_board[row][col] = False
            elif move_type == "cross":
                self.user_board[row][col] = 'X'
                self.error_board[row][col] = False
        else:
            # Mark the cell as error to trigger visual feedback (e.g. red cross overlay)
            self.error_board[row][col] = True
        return valid, message
    
    def get_game_state(self):
        """
        Returns a dictionary containing the current game state.
        This includes the user board, error board, colored board, solution number board, and elapsed time.
        """
        return {
            "user_board": self.user_board,
            "error_board": self.error_board,
            "colored_board": self.colored_board,
            "solution_number_board": self.solution_number_board,
            "elapsed_time": self.get_elapsed_time()
        }
    
    def is_game_complete(self):
        """
        Check if the game is complete: every row has a queen placed at the correct cell.
        
        Returns:
            bool: True if the game is complete, False otherwise.
        """
        for row in range(self.board_size):
            if self.user_board[row][self.solution_queen_board[row]] != 'Q':
                return False
        return True
