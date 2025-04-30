# app/models/conquest_generator.py
"""
Conquest board generator — unrestricted capture logic
=====================================================

Reglas recapituladas
--------------------
● Cada iteración conquista exactamente *una* celda, por parte de un único color
  (round-robin).
● Una celda candidata se descarta solo si:
    1. Es la posición fija de una reina (no se pueden “comer” reinas).
    2. Quitarla al propietario anterior dividiría su territorio
       en islas desconectadas (conectividad Manhattan).
● Tras la conquista se ejecutan los pasos 1-6:
    – Si aparece una solución alternativa ⇒ se revierte la conquista y se
      detiene (tablero final = último válido).
    – Si el solver coloca las N reinas *y* usa step5_and_6() ≥ 1 vez ⇒ éxito.
● Parada adicional: máximo 2·N² conquistas satisfactorias o sin más fronteras.
● La matriz de colores se devuelve como tuplas RGB, compatible con el front-end.
"""

from __future__ import annotations

import random
import time
from collections import deque
from copy import deepcopy
from typing import Deque, Dict, List, Set, Tuple

from app.utils import color_utils
from .generator  import find_alternate
from .queens     import generate_random_board
from .resoution  import SolverState

Coord = Tuple[int, int]
Territories = Dict[int, Set[Coord]]


# ───────────────────────── helpers ──────────────────────────
def _connected(cells: Set[Coord], removed: Coord | None = None) -> bool:
    """True ⇢ *cells* − *removed* forman un solo componente Manhattan."""
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
    board = [[None] * n for _ in range(n)]
    for owner, cells in territories.items():
        rgb = seed_colors[owner]
        for r, c in cells:
            board[r][c] = rgb
    return board


# ───────────────────────── generator ────────────────────────
def generate_conquest_board(
    n: int,
    *,
    max_rounds: int = 2_000,
    debug: bool = False,
):
    # 1 ▸ solución oficial y territorios iniciales
    solution = generate_random_board(n)
    queen_cells: Set[Coord] = {(r, solution[r]) for r in range(n)}

    territories: Territories = {i: {(i, col)} for i, col in enumerate(solution)}
    dominant = random.randrange(n)
    all_cells = {(r, c) for r in range(n) for c in range(n)}
    territories[dominant] = all_cells - (queen_cells - territories[dominant])

    seed_colors = color_utils.generate_distinct_colors(n)
    last_valid = deepcopy(territories)

    colour_queue = list(range(n))
    ptr = 0
    successful = 0
    limit = 2 * n * n

    # 2 ▸ bucle de conquistas
    for it in range(max_rounds):
        if successful >= limit:
            break

        colour = colour_queue[ptr]
        ptr = (ptr + 1) % n
        if colour == dominant and it < n:
            continue   # el dominante se salta la primera vuelta global

        # ── construir frontera ───────────────────────────────────────────
        frontier: List[Coord] = []
        for r, c in territories[colour]:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < n and 0 <= nc < n):
                    continue
                cell = (nr, nc)

                # 1) no podemos conquistar una reina
                if cell in queen_cells:
                    continue
                # 2) evitar gastar turno en una celda que ya nos pertenece
                if cell in territories[colour]:
                    continue

                frontier.append(cell)
        # ────────────────────────────────────────────────────────────────

        if not frontier:
            continue

        random.shuffle(frontier)
        snapshot = deepcopy(territories)
        conquest_made = False

        for cell in frontier:
            old_owner = next(
                (o for o, terr in territories.items() if cell in terr),
                None,
            )
            # 2) no crear isla al antiguo propietario
            if old_owner is not None and not _connected(territories[old_owner], removed=cell):
                continue

            # conquista válida
            territories[colour].add(cell)
            if old_owner is not None:
                territories[old_owner].remove(cell)
            conquest_made = True
            successful += 1
            break

        if not conquest_made:
            continue

        # 3 ▸ comprobaciones de unicidad y dificultad
        coloured = _to_rgb(territories, n, seed_colors)

        solver = SolverState(coloured)
        used_56 = False
        changed = True
        while changed:
            changed = solver.step1() or solver.step2() or solver.step3() or solver.step4()
            if solver.step5_and_6():
                changed = True
                used_56 = True

        # ¿apareció solución alternativa?
        if find_alternate(solution, coloured):
            territories = snapshot      # revertir
            break

        # ¿tablero resuelto con suficiente dificultad?
        if sum(q for row in solver.queens for q in row) == n:
            last_valid = deepcopy(territories)
            break

        last_valid = deepcopy(territories)

        if debug:
            print(f"Iter {it:3}  colour={colour:<2}  conquistas={successful}")

    return solution, _to_rgb(last_valid, n, seed_colors)
