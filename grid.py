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

    # ANSI colors
    _RESET  = "\033[0m"
    _BOLD   = "\033[1m"
    _RED    = "\033[91m"
    _GREEN  = "\033[92m"
    _YELLOW = "\033[93m"
    _CYAN   = "\033[96m"
    _GRAY   = "\033[90m"

    def _cell_str(self, v):
        """Return a colored 3-char string for one cell."""
        if v == self.EMPTY:
            return f"{self._GRAY} · {self._RESET}"
        elif v == self.BLOCKED:
            return f"{self._RED} ▓ {self._RESET}"
        elif v == 'P':
            return f"{self._YELLOW}{self._BOLD} P {self._RESET}"
        elif v == 'R':
            return f"{self._GREEN}{self._BOLD} R {self._RESET}"
        else:                       # driver label e.g. D1, D12
            label = v[:2] if len(v) > 2 else v
            return f"{self._CYAN}{self._BOLD}{label:>2} {self._RESET}"

    def display(self, title=""):
        W = self.cols * 3 + 6       # total inner width
        bar = "═" * W

        # ── title box ────────────────────────────────────────
        print()
        if title:
            pad_l = (W - len(title) - 2) // 2
            pad_r = W - len(title) - 2 - pad_l
            print(f"{self._BOLD}╔{bar}╗{self._RESET}")
            print(f"{self._BOLD}║{' ' * pad_l} {title} {' ' * pad_r}║{self._RESET}")
            print(f"{self._BOLD}╠{bar}╣{self._RESET}")
        else:
            print(f"{self._BOLD}╔{bar}╗{self._RESET}")

        # ── legend ───────────────────────────────────────────
        legend = (
            f"  "
            f"{self._CYAN}{self._BOLD}D{self._RESET}=Driver  "
            f"{self._YELLOW}{self._BOLD}P{self._RESET}=Pickup  "
            f"{self._GREEN}{self._BOLD}R{self._RESET}=Dest  "
            f"{self._RED}▓{self._RESET}=Blocked  "
            f"{self._GRAY}·{self._RESET}=Empty"
        )
        print(f"{self._BOLD}║{self._RESET}{legend}")
        print(f"{self._BOLD}╠{bar}╣{self._RESET}")

        # ── column numbers (small grids only) ────────────────
        show_coords = self.cols <= 30
        if show_coords:
            print(f"{self._BOLD}║{self._RESET}    ", end="")
            for c in range(self.cols):
                print(f"{self._GRAY}{c:3}{self._RESET}", end="")
            print(f"   {self._BOLD}║{self._RESET}")
            print(f"{self._BOLD}║{self._RESET}{'─' * W}{self._BOLD}║{self._RESET}")

        # ── grid rows ────────────────────────────────────────
        for r in range(self.rows):
            if show_coords:
                print(f"{self._BOLD}║{self._RESET}{self._GRAY}{r:3}{self._RESET} ", end="")
            else:
                print(f"{self._BOLD}║{self._RESET}     ", end="")
            for c in range(self.cols):
                print(self._cell_str(self.cells[r][c]), end="")
            print(f"  {self._BOLD}║{self._RESET}")

        # ── bottom ───────────────────────────────────────────
        print(f"{self._BOLD}╚{bar}╝{self._RESET}")
