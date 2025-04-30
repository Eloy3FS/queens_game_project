# app/models/conquest_generator.py

import random
from .queens import generate_random_board
from .coloring import color_board
from .resoution import SolverState
from .generator import find_alternate     # <-- IMPORT CORRECTO

def generate_conquest_board(N, max_iterations=1000):
    """
    Genera tablero usando el 'método de conquista':
    1) Partimos de una solución aleatoria.
    2) Creamos 'territorios' por reina y un dominante que ocupa casi todo.
    3) Iterativamente, cada reina (salvo el dominante en la 1ª vuelta) conquista
       celdas adyacentes libres.
    4) Tras cada conquista, aplicamos los pasos 1–6 de SolverState en bucle.
       - Si sigue única: seguimos conquistando.
       - Si aparecen soluciones alternativas: llamamos a find_alternate(),
         recoloreamos localmente esa celda (como en el método antiguo) y devolvemos.
    """
    # 1) Solución oficial
    solution = generate_random_board(N)

    # 2) Inicialización de territorios
    territories = {i: {(i, solution[i])} for i in range(N)}
    dominant = random.randrange(N)
    all_cells = {(r, c) for r in range(N) for c in range(N)}
    others   = {(r, solution[r]) for r in range(N) if r != dominant}
    territories[dominant] = all_cells - others

    def build_colored():
        board = [[None]*N for _ in range(N)]
        for i, terr in territories.items():
            for (r, c) in terr:
                board[r][c] = i
        return board

    # 3) Bucle de conquista
    for _ in range(max_iterations):
        # Cada reina expande su territorio
        for i in range(N):
            if i == dominant and _ == 0:
                continue
            neighs = set()
            for (r, c) in territories[i]:
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    rr, cc = r+dr, c+dc
                    if 0<=rr<N and 0<=cc<N and all((rr,cc) not in territories[j] for j in range(N)):
                        neighs.add((rr,cc))
            if neighs:
                territories[i].add(random.choice(list(neighs)))

        colored = build_colored()

        # 4) Comprobación determinista
        solver = SolverState(colored)
        changed = True
        while changed:
            changed = (
                solver.step1() or solver.step2() or solver.step3()
                or solver.step4() or solver.step5_and_6()
            )
        placed = sum(1 for row in solver.queens for x in row if x)
        if placed == N:
            continue  # sigue siendo única → más conquistas

        # 5) Si hay alternativa, la corregimos y devolvemos
        alt = find_alternate(solution, colored)
        if alt:
            for r in range(N):
                if alt[r] != solution[r]:
                    c = alt[r]
                    # buscamos colores vecinos distintos para recolorear
                    neigh_cols = []
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        rr, cc = r+dr, c+dc
                        if 0<=rr<N and 0<=cc<N:
                            col = colored[rr][cc]
                            if col is not None and col != colored[r][c]:
                                neigh_cols.append(col)
                    if neigh_cols:
                        old = colored[r][c]
                        new = random.choice(neigh_cols)
                        # actualizamos en territories
                        territories[old].discard((r,c))
                        territories[new].add((r,c))
                    break
            return solution, build_colored()

    # 6) Fallback si no encontramos alternativa
    return solution, build_colored()
