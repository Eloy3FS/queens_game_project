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

from app.utils.color_utils import generate_distinct_colors, find_alternate, plot_colored_board
from app.models.queens import generate_random_board, print_board
from app.models.resoution import SolverState

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
    record_steps: bool = False,
):
    """
    Generate an N×N board with:
      - unique solution
      - requires step5_and_6()
      - no colour islands

    If record_steps=True, devuelve además una lista de todos los tableros
    intermedios y su etiqueta, útil para depuración interactiva.

    Returns:
      solution: List[int]
      final_board: List[List[RGB]]
      iterations: int
      successful_conquests: int
      stop_reason: str
      steps (solo si record_steps=True): List[ (etiqueta: str, board: List[List[RGB]]) ]
    """
    # 1. Official solution & initial territories
    solution = generate_random_board(n)
    queen_cells: Set[Coord] = {(r, solution[r]) for r in range(n)}

    territories: Territories = {i: {(i, solution[i])} for i in range(n)}
    dominant = random.randrange(n)
    all_cells = {(r, c) for r in range(n) for c in range(n)}
    territories[dominant] = all_cells - (queen_cells - territories[dominant])

    # 2. Color seeds & prepare recording
    seed_colors = generate_distinct_colors(n)
    last_valid = deepcopy(territories)

    # Lista para grabar tableros intermedios
    steps: List[Tuple[str, List[List[Tuple[int,int,int]]]]] = []
    if record_steps:
        steps.append(("start", _to_rgb(territories, n, seed_colors)))

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
                if cell in queen_cells or cell in territories[colour]:
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

        # Try a conquest
        for cell in frontier:
            old_owner = next(
                (o for o, terr in territories.items() if cell in terr),
                None,
            )
            # Skip if splits old owner's territory
            if old_owner is not None and not _connected(territories[old_owner], removed=cell):
                continue
            # Perform conquest
            territories[colour].add(cell)
            if old_owner is not None:
                territories[old_owner].remove(cell)
            successful += 1
            conquest_done = True
            break

        if not conquest_done:
            continue

        # Grabar estado post-conquista
        if record_steps:
            steps.append((f"conquest #{successful} @ it{it}", _to_rgb(territories, n, seed_colors)))

        # Post-conquest: solver + alternate check
        coloured = _to_rgb(territories, n, seed_colors)
        solver = SolverState(coloured)
        # used56 = False
        # round = 0

        # # Aplicar pasos lógicos y grabar cada uno
        # while True:
        #     applied = False
        #     # step1..step4
        #     for num, fn in enumerate((solver.step1, solver.step2, solver.step3, solver.step4), start=1):
        #         if fn():
        #             applied = True
        #             if record_steps:
        #                 steps.append((f"step{num} @ it{it} round{round}", _to_rgb(territories, n, seed_colors)))
        #     # step5_and_6
        #     if solver.step5_and_6():
        #         applied = True
        #         used56 = True
        #         if record_steps:
        #             steps.append((f"step5_and_6 @ it{it} round{round}", _to_rgb(territories, n, seed_colors)))
        #     if not applied:
        #         break
        #     round += 1
        # Motor “barato-primero”: devuelve p. ej. [1,2,1,3,1,4,5]
        seq = solver.propagate()
        used56 = 5 in seq
 
        # Registrar cada paso de la traza, igual que antes
        if record_steps and seq:
            for k, step in enumerate(seq):
                tag = "step5_and_6" if step == 5 else f"step{step}"
                steps.append(
                    (f"{tag} @ it{it} idx{k}",
                    _to_rgb(territories, n, seed_colors)))

        # Alternate solution: revert & continue
        if find_alternate(solution, coloured):
            if debug:
                print(f"[debug] alternate solution at it{it}, revert")
            territories = snapshot
            continue

        placed = sum(q for row in solver.queens for q in row)
        # Stop C: solved con dificultad
        # if placed == n and used56:
        #     stop_reason = "solved with step5_and_6"
        #     if debug:
        #         print(f"[stop] {stop_reason} at it{it}")
        #     last_valid = deepcopy(territories)
        #     break

        last_valid = deepcopy(territories)
    else:
        # Stop D: max_rounds reached
        stop_reason = f"max_rounds reached ({max_rounds})"
        if debug:
            print(f"[stop] {stop_reason}")

    # Estado final
    final_board = _to_rgb(last_valid, n, seed_colors)
    return solution, final_board, it + 1, successful, stop_reason, steps


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Queens Conquest Generator")
    parser.add_argument("--size", "-n", type=int, default=8, help="Board size N")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    args = parser.parse_args()

    # Desempaquetamos el sexto valor (_) que es steps cuando record_steps=False
    sol, board, iterations, successful, stop_reason, _ = generate_conquest_board(
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

    # Mostrar la última imagen
    plot_colored_board(board)

    sys.exit(0)
