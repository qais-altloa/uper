# grid.py

class Grid:
    EMPTY   = '0'
    BLOCKED = 'X'

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [[self.EMPTY] * cols for _ in range(rows)]

    # ── helpers ──────────────────────────────────────────────

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_blocked(self, row, col):
        return self.cells[row][col] == self.BLOCKED

    def is_free(self, row, col):
        return self.cells[row][col] == self.EMPTY

    # ── placement ────────────────────────────────────────────

    def place(self, row, col, symbol):
        self.cells[row][col] = symbol

    def clear(self, row, col):
        self.cells[row][col] = self.EMPTY

    def add_obstacle(self, row, col):
        self.cells[row][col] = self.BLOCKED

    # ── display ──────────────────────────────────────────────

    def display(self, title=""):
        if title:
            print(f"\n{'='*40}")
            print(f"  {title}")
        print(f"{'='*40}")

        # column header
        print("     ", end="")
        for c in range(self.cols):
            print(f"{c:3}", end="")
        print()

        for r in range(self.rows):
            print(f"{r:3}  ", end="")
            for c in range(self.cols):
                v = self.cells[r][c]
                if v == self.EMPTY:
                    print("  .", end="")
                elif v == self.BLOCKED:
                    print("  X", end="")
                elif v == 'P':
                    print("  P", end="")
                elif v == 'R':
                    print("  R", end="")
                else:           # driver label e.g. "D1"
                    print(f" {v:>2}", end="")
            print()
        print("=" * 40)
