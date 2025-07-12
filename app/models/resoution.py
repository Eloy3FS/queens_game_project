import unittest
from collections import defaultdict

class SolverState:
    def __init__(self, colored_board):
        self.colored_board = colored_board
        self.N = len(colored_board)
        self.candidates = [[True] * self.N for _ in range(self.N)]
        self.queens = [[False] * self.N for _ in range(self.N)]

    def eliminate_for_queen(self, r, c):
        """Eliminate candidates conflicting with queen at (r,c)."""
        self.candidates[r][c] = False
        for i in range(self.N):
            self.candidates[r][i] = False
            self.candidates[i][c] = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.N and 0 <= cc < self.N:
                    self.candidates[rr][cc] = False
        color = self.colored_board[r][c]
        for i in range(self.N):
            for j in range(self.N):
                if (i, j) != (r, c) and self.colored_board[i][j] == color:
                    self.candidates[i][j] = False

    def place_queen(self, r, c):
        if not self.queens[r][c]:
            self.queens[r][c] = True
            self.eliminate_for_queen(r, c)
            return True
        return False

    @staticmethod
    def simulate_mask_after_placement(candidates, colored_board, r0, c0):
        N = len(colored_board)
        sim = [row[:] for row in candidates]
        sim[r0][c0] = False
        for i in range(N):
            sim[r0][i] = False
            sim[i][c0] = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r0 + dr, c0 + dc
                if 0 <= rr < N and 0 <= cc < N:
                    sim[rr][cc] = False
        color = colored_board[r0][c0]
        for i in range(N):
            for j in range(N):
                if (i, j) != (r0, c0) and colored_board[i][j] == color:
                    sim[i][j] = False
        return sim

    def step1(self):
        changed = False
        color_positions = defaultdict(list)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    color_positions[self.colored_board[i][j]].append((i, j))
        for positions in color_positions.values():
            if len(positions) == 1:
                r, c = positions[0]
                if self.place_queen(r, c):
                    changed = True
        return changed

    def step2(self):
        changed = False
        for i in range(self.N):
            pos = [(i, j) for j in range(self.N) if self.candidates[i][j]]
            if len(pos) == 1:
                r, c = pos[0]
                if self.place_queen(r, c):
                    changed = True
        return changed

    def step3(self):
        changed = False
        # rows uniform
        for i in range(self.N):
            row = self.colored_board[i]
            if all(x == row[0] for x in row):
                color = row[0]
                for r in range(self.N):
                    for c in range(self.N):
                        if r != i and self.candidates[r][c] and self.colored_board[r][c] == color:
                            self.candidates[r][c] = False
                            changed = True
        # columns uniform
        for j in range(self.N):
            col = [self.colored_board[i][j] for i in range(self.N)]
            if all(x == col[0] for x in col):
                color = col[0]
                for r in range(self.N):
                    for c in range(self.N):
                        if c != j and self.candidates[r][c] and self.colored_board[r][c] == color:
                            self.candidates[r][c] = False
                            changed = True
        return changed

    def step4(self):
        changed = False
        # Naked sets in rows
        color_rows = defaultdict(set)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    color_rows[self.colored_board[i][j]].add(i)
        rows_colors = defaultdict(list)
        for color, rows in color_rows.items():
            rows_colors[frozenset(rows)].append(color)
        for rows_set, colors in rows_colors.items():
            k = len(rows_set)
            if k >= 1 and len(colors) == k:
                for r in rows_set:
                    for c in range(self.N):
                        if self.candidates[r][c] and self.colored_board[r][c] not in colors:
                            self.candidates[r][c] = False
                            changed = True
        # Naked sets in columns
        color_cols = defaultdict(set)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    color_cols[self.colored_board[i][j]].add(j)
        cols_colors = defaultdict(list)
        for color, cols in color_cols.items():
            cols_colors[frozenset(cols)].append(color)
        for cols_set, colors in cols_colors.items():
            k = len(cols_set)
            if k >= 1 and len(colors) == k:
                for c in cols_set:
                    for r in range(self.N):
                        if self.candidates[r][c] and self.colored_board[r][c] not in colors:
                            self.candidates[r][c] = False
                            changed = True
        return changed

    # def step5_and_6(self):
    #     """
    #     Elimina cualquier candidata que, al poner una reina en ella, provoque que:
    #     • otro color quede sin candidatas,
    #     • otra fila quede sin candidatas, o
    #     • otra columna quede sin candidatas.
    #     Devuelve True si ha eliminado al menos una casilla.
    #     """
    #     changed = False
    #     N = self.N
    #     colors = {c for row in self.colored_board for c in row}

    #     # --- Conteo PRE-vio de candidatas ---
    #     pre_color = {col: 0 for col in colors}
    #     pre_row   = [0]*N
    #     pre_col   = [0]*N
    #     for r in range(N):
    #         for c in range(N):
    #             if self.candidates[r][c]:
    #                 pre_color[self.colored_board[r][c]] += 1
    #                 pre_row[r] += 1
    #                 pre_col[c] += 1

    #     # --- Revisión de cada casilla candidata ---
    #     for i in range(N):
    #         for j in range(N):
    #             if not self.candidates[i][j]:
    #                 continue

    #             # 1) Simular colocación de la reina
    #             sim = self.simulate_mask_after_placement(
    #                 self.candidates, self.colored_board, i, j
    #             )

    #             # 2) Conteo POST-simulación (solo donde sim[r][c] siga a True)
    #             post_color = {col: 0 for col in colors}
    #             post_row   = [0]*N
    #             post_col   = [0]*N
    #             for r in range(N):
    #                 for c in range(N):
    #                     if sim[r][c]:
    #                         post_color[self.colored_board[r][c]] += 1
    #                         post_row[r] += 1
    #                         post_col[c] += 1

    #             own_color = self.colored_board[i][j]

    #             # --- Regla 1: otro color agotado ---
    #             agota_color = any(
    #                 pre_color[col] > 0 and        # antes había alguna candidata
    #                 col != own_color and          # es “otro” color
    #                 post_color[col] == 0          # después ya no queda
    #                 for col in colors
    #             )

    #             # --- Regla 2: otra fila agotada ---
    #             agota_fila = any(
    #                 pre_row[r] > 0 and            # antes tenía algo
    #                 r != i and                    # no es la fila de la reina
    #                 post_row[r] == 0
    #                 for r in range(N)
    #             )

    #             # --- Regla 3: otra columna agotada ---
    #             agota_col = any(
    #                 pre_col[c] > 0 and
    #                 c != j and
    #                 post_col[c] == 0
    #                 for c in range(N)
    #             )

    #             # 3) Eliminar la casilla si viola alguna regla
    #             if agota_color or agota_fila or agota_col:
    #                 self.candidates[i][j] = False
    #                 changed = True

    #     return changed

    from collections import defaultdict

    def step5_and_6(self):
        """Optimized **Step 5‑6** (O(N³)).

        Para cada casilla candidata «simula» (en tiempo constante ≈ O(N)) la
        colocación de una reina y elimina la casilla si:

        1.   **Otro color** se queda sin opciones.
        2.   **Otra fila** se queda sin opciones.
        3.   **Otra columna** se queda sin opciones.

        La clave de la optimización es **no clonar la máscara completa** cada
        vez.  En su lugar pre‑calculamos contadores y, para cada candidata,
        calculamos cuántas de esas piezas contaría la zona de eliminación
        (fila i, columna j, color propio y 4 diagonales adyacentes).  Basta
        con aritmética sobre esos contadores – no es necesario escanear toda
        la cuadrícula –, lo que reduce el coste total a O(N³).
        """
        N = self.N
        colors = {c for row in self.colored_board for c in row}

        # ────────────────────────────
        # 1.  CONTADORES PRINCIPALES  ─────────────────────────────────────────
        # ────────────────────────────
        pre_color = {col: 0 for col in colors}
        pre_row: list[int] = [0] * N
        pre_col: list[int] = [0] * N
        row_color: list[dict[int, int]] = [defaultdict(int) for _ in range(N)]
        col_color: list[dict[int, int]] = [defaultdict(int) for _ in range(N)]

        for r in range(N):
            for c in range(N):
                if self.candidates[r][c]:
                    clr = self.colored_board[r][c]
                    pre_color[clr] += 1
                    pre_row[r] += 1
                    pre_col[c] += 1
                    row_color[r][clr] += 1
                    col_color[c][clr] += 1

        # ────────────────────────────
        # 2.  RECORRER CANDIDATAS     ─────────────────────────────────────────
        # ────────────────────────────
        to_remove = [[False] * N for _ in range(N)]

        for i in range(N):
            for j in range(N):
                if not self.candidates[i][j]:
                    continue

                own_color = self.colored_board[i][j]

                # 2‑A) ¿Agota otro color?
                exhausts_color = False
                for clr, total in pre_color.items():
                    if clr == own_color or total == 0:
                        continue

                    # Piezas de «clr» eliminadas por la reina.
                    elim = row_color[i].get(clr, 0) + col_color[j].get(clr, 0)

                    # Diagonales (máx. 4 casillas).
                    for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                        rr, cc = i + dr, j + dc
                        if 0 <= rr < N <= cc < 0:  # Trick: always False, avoids nested if
                            pass  # (mantiene layout)
                        elif 0 <= rr < N and 0 <= cc < N and self.candidates[rr][cc] and self.colored_board[rr][cc] == clr:
                            elim += 1

                    if elim >= total:  # se queda a cero
                        exhausts_color = True
                        break

                if exhausts_color:
                    to_remove[i][j] = True
                    continue

                # 2‑B) ¿Agota otra fila?
                exhausts_row = False
                for r in range(N):
                    if r == i or pre_row[r] == 0:
                        continue

                    elim_row = row_color[r].get(own_color, 0)

                    # Casilla (r, j) si es candidata y de color ≠ own_color.
                    if self.candidates[r][j] and self.colored_board[r][j] != own_color:
                        elim_row += 1

                    # Diagonales inmediatas si r está justo encima/abajo.
                    if abs(r - i) == 1:
                        for dc in (-1, 1):
                            cc = j + dc
                            if 0 <= cc < N and self.candidates[r][cc] and self.colored_board[r][cc] != own_color:
                                elim_row += 1

                    if elim_row >= pre_row[r]:
                        exhausts_row = True
                        break

                if exhausts_row:
                    to_remove[i][j] = True
                    continue

                # 2‑C) ¿Agota otra columna?
                exhausts_col = False
                for c in range(N):
                    if c == j or pre_col[c] == 0:
                        continue

                    elim_col = col_color[c].get(own_color, 0)

                    # Casilla (i, c) si es candidata y de color ≠ own_color.
                    if self.candidates[i][c] and self.colored_board[i][c] != own_color:
                        elim_col += 1

                    # Diagonales inmediatas si c está justo izquierda/derecha.
                    if abs(c - j) == 1:
                        for dr in (-1, 1):
                            rr = i + dr
                            if 0 <= rr < N and self.candidates[rr][c] and self.colored_board[rr][c] != own_color:
                                elim_col += 1

                    if elim_col >= pre_col[c]:
                        exhausts_col = True
                        break

                if exhausts_col:
                    to_remove[i][j] = True
                    # continue  # no hace falta, ya no hay más reglas

        # ────────────────────────────
        # 3.  APLICAR ELIMINACIONES  ─────────────────────────────────────────
        # ────────────────────────────
        changed = False
        for r in range(N):
            for c in range(N):
                if to_remove[r][c]:
                    self.candidates[r][c] = False
                    changed = True

        return changed



    
    def propagate(self):
        """
        Ejecuta los pasos 1-6 de menor a mayor coste hasta que ninguno de los
        pasos 2-6 produzca más cambios.
        Devuelve la secuencia de pasos que *sí* han modificado el tablero,
        por ejemplo  [1, 2, 1, 3, 1, 4, 5].
        """
        seq: list[int] = []
        while True:
            # — Paso 1 (no reinicia el ciclo) —
            if self.step1():
                seq.append(1)
                continue


            # — Paso 2 —
            if self.step2():
                seq.append(2)
                continue           # vuelva a empezar desde 1

            # — Paso 3 —
            if self.step3():
                seq.append(3)
                continue

            # — Paso 4 —
            if self.step4():
                seq.append(4)
                continue

            # — Paso 5-6 —
            if self.step5_and_6():   # se cuentan como «5»
                seq.append(5)
                continue

            # Ninguno de los pasos 2-6 cambió nada ⇒ terminado
            break
        return seq



class TestResolutionSteps(unittest.TestCase):
    def test_step1(self):
        cb = [[1, 2], [1, 3]]
        s = SolverState(cb)
        self.assertTrue(s.step1())
        self.assertTrue(s.queens[0][1])

    def test_step2(self):
        cb = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        s = SolverState(cb)
        s.candidates = [[False, True, False], [True, True, True], [True, True, True]]
        self.assertTrue(s.step2())
        self.assertTrue(s.queens[0][1])

    def test_step3(self):
        cb = [[5, 5], [5, 6]]
        s = SolverState(cb)
        self.assertTrue(s.step3())
        self.assertFalse(s.candidates[1][0])

    def test_step4_simple(self):
        cb = [[10, 11, 12], [10, 11, 13], [14, 15, 16]]
        s = SolverState(cb)
        self.assertTrue(s.step4())
        self.assertFalse(s.candidates[0][0])
        self.assertFalse(s.candidates[0][1])
        self.assertTrue(s.candidates[0][2])

    def test_step4_naked(self):
        cb = [[1, 2, 3], [1, 2, 4], [1, 2, 5]]
        s = SolverState(cb)
        self.assertFalse(s.step4())
        cb2 = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        s2 = SolverState(cb2)
        self.assertTrue(s2.step4())

    def test_step5_and_6(self):
        cb = [[100, 200], [200, 100]]
        s = SolverState(cb)
        self.assertTrue(s.step5_and_6())
        self.assertFalse(s.candidates[0][0])
        cb2 = [[1, 2], [3, 4]]
        s2 = SolverState(cb2)
        s2.candidates = [[True, False], [True, True]]
        self.assertTrue(s2.step5_and_6())
        self.assertFalse(s2.candidates[1][0])

if __name__ == '__main__':
    unittest.main()
