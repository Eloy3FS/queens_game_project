import random
import multiprocessing
from app.models.queens import generate_random_board
from app.models.coloring import color_board
from app.models.resoution import SolverState
import colorsys



def _conflicts(positions, row, col, colored_board):
    """
    Check if placing a queen at (row, col) conflicts with existing positions.
    """
    for (r, c) in positions:
        # row or column conflict
        if r == row or c == col:
            return True
        # adjacency conflict
        if max(abs(r - row), abs(c - col)) == 1:
            return True
        # same color region conflict
        if colored_board[r][c] == colored_board[row][col]:
            return True
    return False


def _dfs(row, positions, official_solution, colored_board, N):
    """
    Depth-first search for an alternate solution.
    """
    if row == N:
        sol = [None] * N
        for r, c in positions:
            sol[r] = c
        # ensure different from official
        return sol if sol != official_solution else None

    for col in range(N):
        # skip used columns
        if any(c == col for (_, c) in positions):
            continue
        # skip conflicts
        if _conflicts(positions, row, col, colored_board):
            continue
        positions.add((row, col))
        result = _dfs(row + 1, positions, official_solution, colored_board, N)
        if result:
            return result
        positions.remove((row, col))
    return None


def _search_task(args):
    """
    Worker function for multiprocessing: attempts DFS starting from row 0 at given col0.
    """
    official_solution, colored_board, col0 = args
    N = len(colored_board)
    # initial position at row0
    positions = {(0, col0)}
    return _dfs(1, positions, official_solution, colored_board, N)


def find_alternate(official_solution, colored_board):
    """
    Parallelized attempt to find an alternate solution different from the official one.
    Returns a list of column indices per row if found, else None.

    This uses a process pool equal to cpu_count() to search different starting columns.
    """
    N = len(colored_board)
    # prepare tasks for each candidate in row 0 (excluding official)
    candidates = [col for col in range(N) if col != official_solution[0]]
    tasks = [(official_solution, colored_board, col0) for col0 in candidates]

    # use a pool of workers
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for result in pool.imap_unordered(_search_task, tasks):
            if result:
                # early exit: found alternate
                pool.terminate()
                return result
    return None


def generate_unique_board(N, max_iterations=1000):
    """
    Generate a board (solution and colored_board) that has a unique solution
    under the deterministic resolution rules (steps 1-6 combined efficiently).

    Returns:
        tuple: (solution_list, colored_board matrix)
    """
    for _ in range(max_iterations):
        # random solution
        solution = generate_random_board(N)
        # initial coloring
        colored_board, _ = color_board(solution, N)

        # deterministic resolution
        solver = SolverState(colored_board)
        changed = True
        while changed:
            changed = (
                solver.step1() or solver.step2() or solver.step3() or
                solver.step4() or solver.step5_and_6()
            )

        # check fully solved
        placed = sum(1 for row in solver.queens for x in row if x)
        if placed == N:
            return solution, colored_board

        # test for alternate solution
        alt = find_alternate(solution, colored_board)
        if alt:
            # recolor first differing cell
            for r in range(N):
                if alt[r] != solution[r]:
                    c = alt[r]
                    neighbors = []
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < N and 0 <= cc < N:
                            col = colored_board[rr][cc]
                            if col != colored_board[r][c]:
                                neighbors.append(col)
                    if neighbors:
                        colored_board[r][c] = random.choice(neighbors)
                    break
            continue

        # unique -> return
        return solution, colored_board

    raise RuntimeError(f"Could not generate a unique board in {max_iterations} iterations")

def generate_distinct_colors(n):
    """
    Generate `n` visually distinct RGB colors and return them in shuffled order.
    """
    hues = [i / n for i in range(n)]
    colors = [colorsys.hsv_to_rgb(h, 0.7, 0.95) for h in hues]
    rgb_colors = [tuple(int(c * 255) for c in color) for color in colors]
    random.shuffle(rgb_colors)
    return rgb_colors


def plot_colored_board(board):
    """
    Display a colored board using matplotlib.
    Args:
        board (list of list of (R, G, B)): Board of RGB tuples.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    n = len(board)
    image = [[(r / 255, g / 255, b / 255) for (r, g, b) in row] for row in board]
    plt.figure(figsize=(n / 2.5, n / 2.5))
    plt.imshow(image, interpolation='nearest')
    plt.xticks([])
    plt.yticks([])
    plt.title(f"Colored Board ({n}×{n})")
    plt.show()

import math

def rgb_distance(c1, c2):
    """Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def is_color_distinct(c, others, threshold=100):
    """Check if a color is distinct enough from all others."""
    return all(rgb_distance(c, o) > threshold for o in others)

def random_color():
    """Generate a random RGB color."""
    return tuple(random.randint(0, 255) for _ in range(3))

def hsv_to_rgb(h, s, v):
    """Convert HSV [0-1] to RGB [0-255]."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)
