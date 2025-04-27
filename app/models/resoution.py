import unittest
from collections import defaultdict

class SolverState:
    def __init__(self, colored_board):
        self.colored_board = colored_board
        self.N = len(colored_board)
        self.candidates = [[True for _ in range(self.N)] for __ in range(self.N)]
        self.queens = [[False for _ in range(self.N)] for __ in range(self.N)]

    def eliminate_for_queen(self, r, c):
        """Eliminate candidates conflicting with queen at (r,c)."""
        # remove candidate at queen pos
        self.candidates[r][c] = False
        # row and col elimination
        for i in range(self.N):
            self.candidates[r][i] = False
            self.candidates[i][c] = False
        # adjacency elimination (8 directions)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr==0 and dc==0: continue
                rr = r + dr
                cc = c + dc
                if 0 <= rr < self.N and 0 <= cc < self.N:
                    self.candidates[rr][cc] = False
        # color region elimination
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
        sim = [[c for c in row] for row in candidates]
        # simulate elimination
        # remove candidate at placement
        sim[r0][c0] = False
        # row and col
        for i in range(N):
            sim[r0][i] = False
            sim[i][c0] = False
        # adjacency
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                rr=r0+dr; cc=c0+dc
                if 0<=rr<N and 0<=cc<N:
                    sim[rr][cc] = False
        # region
        color = colored_board[r0][c0]
        for i in range(N):
            for j in range(N):
                if (i,j)!=(r0,c0) and colored_board[i][j]==color:
                    sim[i][j] = False
        return sim

    def step1(self):
        """If only one candidate of a color remains, place queen there."""
        changed=False
        color_positions = defaultdict(list)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    color_positions[self.colored_board[i][j]].append((i,j))
        for positions in color_positions.values():
            if len(positions) == 1:
                r,c = positions[0]
                if self.place_queen(r,c):
                    changed=True
        return changed

    def step2(self):
        """If only one candidate in a row, place queen there."""
        changed=False
        for i in range(self.N):
            positions = [(i,j) for j in range(self.N) if self.candidates[i][j]]
            if len(positions)==1:
                r,c=positions[0]
                if self.place_queen(r,c):
                    changed=True
        return changed

    def step3(self):
        """If a row or column is uniform color, eliminate that color outside it."""
        changed=False
        # rows
        for i in range(self.N):
            row_colors = [self.colored_board[i][j] for j in range(self.N)]
            if all(c==row_colors[0] for c in row_colors):
                color=row_colors[0]
                for r in range(self.N):
                    for c in range(self.N):
                        if r!=i and self.colored_board[r][c]==color and self.candidates[r][c]:
                            self.candidates[r][c]=False
                            changed=True
        # columns
        for j in range(self.N):
            col_colors=[self.colored_board[i][j] for i in range(self.N)]
            if all(c==col_colors[0] for c in col_colors):
                color=col_colors[0]
                for r in range(self.N):
                    for c in range(self.N):
                        if c!=j and self.colored_board[r][c]==color and self.candidates[r][c]:
                            self.candidates[r][c]=False
                            changed=True
        return changed

    def step4(self):
        """If a color appears only in one row, eliminate other colors in that row."""
        changed=False
        color_rows=defaultdict(set)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    color=self.colored_board[i][j]
                    color_rows[color].add(i)
        for color, rows in color_rows.items():
            if len(rows)==1:
                r=list(rows)[0]
                for c in range(self.N):
                    if self.candidates[r][c] and self.colored_board[r][c]!=color:
                        self.candidates[r][c]=False
                        changed=True
        return changed

    def step5(self):
        """Eliminate placements that remove all candidates of any color."""
        to_eliminate=[]
        colors=set(c for row in self.colored_board for c in row)
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    sim = self.simulate_mask_after_placement(self.candidates, self.colored_board, i,j)
                    for color in colors:
                        has=False
                        for r in range(self.N):
                            for c in range(self.N):
                                if sim[r][c] and self.colored_board[r][c]==color:
                                    has=True; break
                            if has: break
                        if not has:
                            to_eliminate.append((i,j))
                            break
        changed=False
        for i,j in to_eliminate:
            if self.candidates[i][j]:
                self.candidates[i][j]=False
                changed=True
        return changed

    def step6(self):
        """Eliminate placements that remove all candidates of any row or column."""
        to_eliminate=[]
        for i in range(self.N):
            for j in range(self.N):
                if self.candidates[i][j]:
                    sim = self.simulate_mask_after_placement(self.candidates, self.colored_board, i,j)
                    bad=False
                    for r in range(self.N):
                        if r==i: continue
                        if not any(sim[r][c] for c in range(self.N)):
                            bad=True; break
                    if not bad:
                        for c in range(self.N):
                            if c==j: continue
                            if not any(sim[r][c] for r in range(self.N)):
                                bad=True; break
                    if bad:
                        to_eliminate.append((i,j))
        changed=False
        for i,j in to_eliminate:
            if self.candidates[i][j]:
                self.candidates[i][j]=False
                changed=True
        return changed

class TestResolutionSteps(unittest.TestCase):
    def test_step1(self):
        cb=[[1,2],[1,3]]
        s=SolverState(cb)
        changed=s.step1()
        self.assertTrue(changed)
        self.assertTrue(s.queens[0][1])

    def test_step2(self):
        cb=[[0,0,0],[0,0,0],[0,0,0]]
        s=SolverState(cb)
        s.candidates=[[False,True,False],[True,True,True],[True,True,True]]
        changed=s.step2()
        self.assertTrue(changed)
        self.assertTrue(s.queens[0][1])

    def test_step3(self):
        cb=[[5,5],[5,6]]
        s=SolverState(cb)
        changed=s.step3()
        self.assertTrue(changed)
        self.assertFalse(s.candidates[1][0])

    def test_step4(self):
        cb=[[10,11,12],[10,11,13],[14,15,16]]
        s=SolverState(cb)
        changed=s.step4()
        self.assertTrue(changed)
        # in row0, only color 12 remains at (0,2)
        self.assertFalse(s.candidates[0][0])
        self.assertFalse(s.candidates[0][1])
        self.assertTrue(s.candidates[0][2])

    def test_step5(self):
        cb=[[100,200],[200,100]]
        s=SolverState(cb)
        changed=s.step5()
        self.assertTrue(changed)
        self.assertFalse(s.candidates[0][0])

    def test_step6(self):
        cb=[[1,2],[3,4]]
        s=SolverState(cb)
        s.candidates=[[True,False],[True,True]]
        changed=s.step6()
        self.assertTrue(changed)
        self.assertFalse(s.candidates[1][0])

if __name__=='__main__':
    unittest.main()
