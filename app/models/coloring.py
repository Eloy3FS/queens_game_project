import random
from app.utils import color_utils
from app.models import queens




def get_neighbors(row, col, N):
    """
    Get valid neighbor positions (Manhattan distance 1) in an N x N board.
    
    Args:
        row (int): Row index.
        col (int): Column index.
        N (int): Board size.
    
    Returns:
        list: List of (row, col) tuples for neighbors.
    """
    neighbors = []
    if row > 0:
        neighbors.append((row - 1, col))
    if row < N - 1:
        neighbors.append((row + 1, col))
    if col > 0:
        neighbors.append((row, col - 1))
    if col < N - 1:
        neighbors.append((row, col + 1))
    return neighbors

def initialize_colored_board(queen_board, N, seed_colors):
    """
    Initialize the colored board with seed colors in the queen positions.
    Also creates a number board with queen numbers (1 to N) in those positions.
    
    Args:
        queen_board (list): List of queen column positions for each row.
        N (int): Board size.
        seed_colors (list): List of distinct colors for each queen.
    
    Returns:
        tuple: (colored_board, number_board)
          - colored_board: N x N matrix with color tuples at queen positions and None elsewhere.
          - number_board: N x N matrix with queen numbers at queen positions and 0 elsewhere.
    """
    colored_board = [[None for _ in range(N)] for _ in range(N)]
    number_board = [[0 for _ in range(N)] for _ in range(N)]
    
    for i, col in enumerate(queen_board):
        colored_board[i][col] = seed_colors[i]
        number_board[i][col] = i + 1  # Queen numbers from 1 to N
    return colored_board, number_board

def color_board(queen_board, N):
    """
    Color the board starting from the queen positions.
    Each queen (number) is associated with a distinct seed color.
    Then, repeatedly, a random seed color is selected, and one of its adjacent
    uncolored cells (Manhattan distance 1) is filled with that color.
    
    Args:
        queen_board (list): List of queen positions (output from queens.py).
        N (int): Board size.
    
    Returns:
        tuple: (colored_board, number_board)
          - colored_board: N x N matrix of color tuples.
          - number_board: N x N matrix with queen numbers in queen positions.
    """
    # Generate distinct colors for each queen
    seed_colors = color_utils.generate_distinct_colors(N)
    
    colored_board, number_board = initialize_colored_board(queen_board, N, seed_colors)
    
    total_cells = N * N
    colored_count = N  # initial colored cells from queens
    
    while colored_count < total_cells:
        # Randomly select a seed color index
        color_index = random.randint(0, N - 1)
        current_color = seed_colors[color_index]
        
        # Find all uncolored candidate cells adjacent to any cell with current_color
        candidates = []
        for r in range(N):
            for c in range(N):
                if colored_board[r][c] is None:
                    for nr, nc in get_neighbors(r, c, N):
                        if colored_board[nr][nc] == current_color:
                            candidates.append((r, c))
                            break
        
        if candidates:
            r, c = random.choice(candidates)
            colored_board[r][c] = current_color
            colored_count += 1
        # If no candidate is found for this color, continue to next iteration.
    
    return colored_board, number_board

# --- Unit Tests ---

import unittest

def matrix_to_string(matrix):
    """
    Convert a matrix into a string representation.
    For colored_board, RGB tuples are converted to hex strings.
    
    Args:
        matrix (list): 2D list (matrix) to convert.
    
    Returns:
        str: String representation of the matrix.
    """
    lines = []
    for row in matrix:
        line = []
        for cell in row:
            if cell is None:
                line.append("None")
            elif isinstance(cell, tuple):
                line.append('#{:02x}{:02x}{:02x}'.format(cell[0], cell[1], cell[2]))
            else:
                line.append(str(cell))
        lines.append(" ".join(line))
    return "\n".join(lines)

class TestColoring(unittest.TestCase):
    def test_coloring_board(self):
        """
        Test the coloring algorithm by generating a queen board,
        converting queen positions to numbers, and then filling the board with colors.
        It prints both the queen number board and the colored board.
        """
        N = 8
        # Generate a queen board (list of column indices for each row)
        queen_board = queens.generate_random_board(N)
        colored_board, number_board = color_board(queen_board, N)
        
        print("Queen Number Board:")
        print(matrix_to_string(number_board))
        print("\nColored Board:")
        print(matrix_to_string(colored_board))
        
        # Assert that the colored board is fully filled (no None values)
        for row in colored_board:
            for cell in row:
                self.assertIsNotNone(cell)
        
        # Assert that the queen positions have the correct seed colors
        # (Since generate_distinct_colors is deterministic, re-generating it gives the same colors)
        seed_colors = color_utils.generate_distinct_colors(N)
        for i, col in enumerate(queen_board):
            self.assertEqual(colored_board[i][col], seed_colors[i])
            
if __name__ == '__main__':
    unittest.main(exit=False)
