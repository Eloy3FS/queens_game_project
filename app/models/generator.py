import random

from .queens import generate_random_board
from .coloring import color_board
from .resoution import SolverState


def find_alternate(official_solution, colored_board):
    """
    Attempt to find an alternative solution different from the official one.
    Returns a list of column indices per row if found, else None.
    """
    N = len(colored_board)
    def conflicts(positions, row, col):
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

    def dfs(row, positions):
        if row == N:
            sol = [None] * N
            for r, c in positions:
                sol[r] = c
            return sol if sol != official_solution else None
        for col in range(N):
            if any(c == col for (_, c) in positions):
                continue
            if conflicts(positions, row, col):
                continue
            positions.add((row, col))
            result = dfs(row + 1, positions)
            if result:
                return result
            positions.remove((row, col))
        return None

    return dfs(0, set())


def generate_unique_board(N, max_iterations=1000):
    """
    Generate a board (solution and colored_board) that has a unique solution
    under the deterministic resolution rules (steps 1-6 combined efficiently).

    Args:
        N (int): board size
        max_iterations (int): max loops to try before giving up

    Returns:
        tuple: (solution_list, colored_board matrix)
    """
    for _ in range(max_iterations):
        # 1) Random solution
        solution = generate_random_board(N)
        # 2) Initial coloring
        colored_board, _ = color_board(solution, N)

        # 3) Deterministic resolution
        solver = SolverState(colored_board)
        changed = True
        while changed:
            changed = (
                solver.step1() or
                solver.step2() or
                solver.step3() or
                solver.step4() or
                solver.step5_and_6()
            )

        # 4) Check if fully solved by rules (one queen per row)
        placed = sum(1 for row in solver.queens for x in row if x)
        if placed == N:
            return solution, colored_board

        # 5) Test for alternate solution
        alt = find_alternate(solution, colored_board)
        if alt:
            # Modify the color of the first differing position
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

        # No alternate found → unique board
        return solution, colored_board

    raise RuntimeError(f"Could not generate a unique board in {max_iterations} iterations")
