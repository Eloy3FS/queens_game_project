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

    def step5_and_6(self):
        """
        Combine step5 and step6: eliminate any candidate that
        1) leaves a color without candidates, or
        2) leaves another row or column without candidates.
        """
        to_elim = []
        colors = {c for row in self.colored_board for c in row}
        for i in range(self.N):
            for j in range(self.N):
                if not self.candidates[i][j]:
                    continue
                sim = self.simulate_mask_after_placement(
                    self.candidates, self.colored_board, i, j
                )
                # check color exhaustion
                fail = any(
                    not any(
                        sim[r][c] and self.colored_board[r][c] == color
                        for r in range(self.N) for c in range(self.N)
                    )
                    for color in colors
                )
                # check row/column exhaustion
                if not fail:
                    if any(
                        not any(sim[r][c] for c in range(self.N))
                        for r in range(self.N) if r != i
                    ) or any(
                        not any(sim[r][c] for r in range(self.N))
                        for c in range(self.N) if c != j
                    ):
                        fail = True
                if fail:
                    to_elim.append((i, j))
        changed = False
        for i, j in to_elim:
            if self.candidates[i][j]:
                self.candidates[i][j] = False
                changed = True
        return changed

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
