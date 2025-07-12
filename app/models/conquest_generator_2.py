# Archivo dessactualizado es necesario actualizar la logica y hacerla más similar al conquest_generator original
#!/usr/bin/env python3
"""
Conquest board generator — standalone executable

Usage:
  python conquest_generator.py --size N [--debug]

Generates an N×N Queens conquest board with unique solution,
ensures no colour islands, logs stop condition and prints the
final queen placement and RGB-coloured board.
"""
import os
import sys

# Ensure project root on sys.path for 'app' imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import random
from collections import deque
from copy import deepcopy
from typing import Deque, Dict, List, Set, Tuple

from app.utils.color_utils import generate_distinct_colors
from app.models.generator import find_alternate
from app.models.queens import generate_random_board, print_board
from app.models.resoution import SolverState

from app.utils.color_utils import plot_colored_board

Coord = Tuple[int, int]
Territories = Dict[int, Set[Coord]]


def _connected(cells: Set[Coord], removed: Coord | None = None) -> bool:
    """Return True if cells (minus removed) form one Manhattan-connected component."""
    if removed:
        cells = cells - {removed}
    if len(cells) <= 1:
        return True
    start = next(iter(cells))
    q: Deque[Coord] = deque([start])
    seen = {start}
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + dr, c + dc)
            if n in cells and n not in seen:
                seen.add(n)
                q.append(n)
    return seen == cells



def _find_island(cells: Set[Coord], queen: Coord) -> Set[Coord]:
    """
    Encuentra la isla en `cells` que no contiene la coordenada `queen`.
    Si no hay tal isla, retorna set vacío.
    """
    if queen not in cells or len(cells) <= 1:
        return set()
    visited = set()
    from collections import deque
    q: Deque[Coord] = deque([queen])
    visited.add(queen)
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) in cells and (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append((nr, nc))
    return cells - visited

def _to_rgb(
    territories: Territories,
    n: int,
    seed_colors: List[Tuple[int, int, int]],
) -> List[List[Tuple[int, int, int]]]:
    """Convert territories to N×N RGB matrix."""
    board: List[List[Tuple[int, int, int] | None]] = [[None] * n for _ in range(n)]
    for owner, cells in territories.items():
        rgb = seed_colors[owner]
        for r, c in cells:
            board[r][c] = rgb
    return board  # type: ignore


def generate_conquest_board(
    n: int,
    *,
    max_rounds: int = 2000,
    debug: bool = False,
) -> Tuple[List[int], List[List[Tuple[int, int, int]]], int, int, str]:
    """
    Generate an N×N board with:
      - unique solution
      - requires step5_and_6()
      - no colour islands
    Returns:
      solution: List[int]
      final_board: List[List[RGB]]
      iterations: int
      successful_conquests: int
      stop_reason: str
    """
    # 1. Official solution & initial territories
    solution = generate_random_board(n)
    queen_cells: Set[Coord] = {(r, solution[r]) for r in range(n)}

    territories: Territories = {i: {(i, solution[i])} for i in range(n)}
    dominant = random.randrange(n)
    all_cells = {(r, c) for r in range(n) for c in range(n)}
    territories[dominant] = all_cells - (queen_cells - territories[dominant])

    # 2. Color seeds for each queen
    seed_colors = generate_distinct_colors(n)
    last_valid = deepcopy(territories)

    colour_queue = list(range(n))
    ptr = 0
    successful = 0
    conquest_limit = 2 * n * n
    stop_reason = ""

    # 3. Conquest loop
    for it in range(max_rounds):
        # Stop A: conquest limit reached
        if successful >= conquest_limit:
            stop_reason = f"conquest limit {conquest_limit}"
            if debug:
                print(f"[stop] {stop_reason}")
            break

        colour = colour_queue[ptr]
        ptr = (ptr + 1) % n
        # Dominant queen skips first cycle
        if colour == dominant and it < n:
            continue

        # Build frontier
        frontier: List[Coord] = []
        for r, c in territories[colour]:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < n and 0 <= nc < n):
                    continue
                cell = (nr, nc)
                # Skip fixed queen spots
                if cell in queen_cells:
                    continue
                # Skip own cells
                if cell in territories[colour]:
                    continue
                frontier.append(cell)

        # Stop B: no moves available globally
        if not frontier:
            can_move = False
            for qcol in colour_queue:
                for rr, cc in territories[qcol]:
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nn = (rr + dr, cc + dc)
                        if 0 <= nn[0] < n and 0 <= nn[1] < n and nn not in queen_cells:
                            can_move = True
                            break
                    if can_move:
                        break
                if can_move:
                    break
            if not can_move:
                stop_reason = "no moves available"
                if debug:
                    print(f"[stop] {stop_reason}")
                break
            continue

        random.shuffle(frontier)
        snapshot = deepcopy(territories)
        conquest_done = False

        for cell in frontier:
            old_owner = next(
                (o for o, terr in territories.items() if cell in terr),
                None,
            )
            # Eliminar la celda del territorio original si existe
            if old_owner is not None:
                territories[old_owner].remove(cell)
            # Conquistar celda principal
            territories[colour].add(cell)
            # Detectar y absorber isla desconectada
            if old_owner is not None:
                island = _find_island(territories[old_owner], (old_owner, solution[old_owner]))
                if island:
                    for iso in island:
                        territories[colour].add(iso)
                        territories[old_owner].remove(iso)
            successful += 1
            conquest_done = True
            break

        if not conquest_done:
            continue

        # Post-conquest: solver + alternate check
        coloured = _to_rgb(territories, n, seed_colors)
        solver = SolverState(coloured)
        # used56 = False
        # changed = True
        # while changed:
        #     changed = (
        #         solver.step1() or solver.step2() or solver.step3() or solver.step4()
        #     )
        #     if solver.step5_and_6():
        #         changed = True
        #         used56 = True
        seq = solver.propagate()
        used56 = 5 in seq

        # Alternate solution: revert & continue
        if find_alternate(solution, coloured):
            if debug:
                print(f"[debug] alternate solution detected at iteration {it}, reverting conquest")
            territories = snapshot
            continue

        placed = sum(q for row in solver.queens for q in row)
        # Stop C: solved with required difficulty
        if placed == n and used56:
            stop_reason = "solved with step5_and_6"
            if debug:
                print(f"[stop] {stop_reason} at iteration {it}")
            last_valid = deepcopy(territories)
            break

        last_valid = deepcopy(territories)
    else:
        # Stop D: max_rounds reached
        stop_reason = f"max_rounds reached ({max_rounds})"
        if debug:
            print(f"[stop] {stop_reason}")

    final_board = _to_rgb(last_valid, n, seed_colors)
    return solution, final_board, it + 1, successful, stop_reason


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Queens Conquest Generator")
    parser.add_argument("--size", "-n", type=int, default=8, help="Board size N")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    args = parser.parse_args()

    sol, board, iterations, successful, stop_reason = generate_conquest_board(
        args.size, debug=args.debug
    )

    # Always print summary in standalone mode
    print(f"\n-- Generation complete: N={args.size} --")
    print(f"Iterations: {iterations}")
    print(f"Successful conquests: {successful}")
    print(f"Stop reason: {stop_reason}\n")

    # Print queen solution
    print("Final queen positions:")
    print_board(sol, args.size)

    # Print colored board as RGB tuples
    print("\nColored board (RGB tuples):")
    for row in board:
        print(" ".join(str(c) for c in row))

    plot_colored_board(board)

    sys.exit(0)