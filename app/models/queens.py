import random
import unittest


def get_allowed_columns(row, board, used_columns, N):
    """
    Calculate allowed columns for the queen in the current row.
    Allowed columns are those not already used and not in the immediate diagonal 
    positions relative to the queen in the previous row.
    
    Args:
        row (int): The current row index.
        board (list): List of chosen column positions for previous rows.
        used_columns (set): Set of columns already used.
        N (int): Size of the board (N x N).
    
    Returns:
        list: A list of allowed column indices.
    """
    # Start with columns that have not been used yet.
    allowed = set(range(N)) - used_columns

    # If there is a previous row, remove immediate diagonal positions
    if row > 0:
        last_col = board[row - 1]
        # Remove the column to the left of the queen in the previous row (if within bounds)
        if (last_col - 1) in allowed:
            allowed.remove(last_col - 1)
        # Remove the column to the right of the queen in the previous row (if within bounds)
        if (last_col + 1) in allowed:
            allowed.remove(last_col + 1)
    
    return list(allowed)

def generate_random_board(N):
    """
    Generate a board with N queens on an N x N matrix.
    Each queen is placed such that:
      - There is exactly one queen per row and per column.
      - No queen is placed in an immediately diagonal cell relative to the queen in the previous row.
    
    The board is generated row by row. For row 0, a random column is chosen.
    For each subsequent row, a random column is chosen from the allowed columns.
    If at any row no allowed column exists, the board generation is restarted.
    
    Args:
        N (int): Size of the board (N x N). 
                 Valid values: N == 1 or N >= 4. (No valid board exists for N=2 or N=3)
    
    Returns:
        list: A list of integers where each integer represents the column position of the queen for that row.
    """
    if N <= 0:
        raise ValueError("Board size N must be positive")
    # For N=2 or N=3, no valid board exists with the immediate diagonal constraint
    if N != 1 and N < 4:
        raise ValueError(f"No valid board exists for N = {N} with immediate diagonal constraints")
    
    while True:
        board = []           # List to store the column index for each row's queen
        used_columns = set() # Set to track columns that are already occupied
        valid = True
        
        for row in range(N):
            allowed = get_allowed_columns(row, board, used_columns, N)
            if not allowed:
                valid = False
                break  # Restart board generation if no allowed column exists in this row
            chosen = random.choice(allowed)
            board.append(chosen)
            used_columns.add(chosen)
        
        if valid:
            return board

def board_to_matrix(board, N):
    """
    Convert the board representation into a matrix format.
    'Q' represents a queen and '.' an empty cell.
    
    Args:
        board (list): List of column positions for queens.
        N (int): Size of the board.
    
    Returns:
        list: A 2D list (matrix) representation of the board.
    """
    matrix = []
    for row in range(N):
        row_list = []
        for col in range(N):
            if board[row] == col:
                row_list.append("Q")
            else:
                row_list.append(".")
        matrix.append(row_list)
    return matrix

def print_board(board, N):
    """
    Print the board in a human-readable format.
    
    Args:
        board (list): List of queen column positions.
        N (int): Size of the board.
    """
    matrix = board_to_matrix(board, N)
    for row in matrix:
        print(" ".join(row))

# --- Unit Tests ---

class TestQueensGeneration(unittest.TestCase):
    def test_valid_board(self):
        """Test that a valid board is generated for N = 8."""
        N = 8
        board = generate_random_board(N)
        # Check the board length
        self.assertEqual(len(board), N)
        # Check that all columns are unique
        self.assertEqual(len(set(board)), N)
        # Check that no queen is placed in an immediate diagonal relative to the previous row
        for i in range(1, N):
            prev = board[i - 1]
            current = board[i]
            self.assertNotEqual(current, prev - 1)
            self.assertNotEqual(current, prev + 1)

    def test_single_cell_board(self):
        """Test that the board for N = 1 is correctly generated."""
        N = 1
        board = generate_random_board(N)
        self.assertEqual(board, [0])
    
    def test_invalid_board_size(self):
        """Test that board generation fails for N=2 and N=3."""
        with self.assertRaises(ValueError):
            generate_random_board(2)
        with self.assertRaises(ValueError):
            generate_random_board(3)

if __name__ == '__main__':
    # Generate and print a sample board for visual confirmation
    board = generate_random_board(8)
    print("Generated board (N=8):")
    print_board(board, 8)
    
    # Run unit tests
    unittest.main(exit=False)
