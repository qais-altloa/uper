# admin.py
# Admin panel: add, remove, edit drivers — persisted to drivers.txt
# File format (one driver per line): id,name,phone,car,row,col

from models import Driver

class DriversFile:

    def __init__(self, filepath="drivers.txt"):
        self.filepath = filepath

    # ── read ──────────────────────────────────

    def load(self):
        """Read drivers.txt → list of Driver objects. Returns [] if file missing."""
        drivers = []
        try:
            with open(self.filepath, "r") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) != 6:
                        print(f"  [!] Skipping malformed line {line_num} in {self.filepath}: '{line}'")
                        continue
                    id_, name, phone, car, row, col = parts
                    if not row.lstrip('-').isdigit() or not col.lstrip('-').isdigit():
                        print(f"  [!] Skipping line {line_num}: row/col must be integers (got '{row}', '{col}')")
                        continue
                    drivers.append(Driver(id_, name, phone, car, int(row), int(col)))
        except FileNotFoundError:
            pass   # first run — file not created yet
        return drivers

    # ── write ─────────────────────────────────

    def save(self, drivers):
        """Write list of Driver objects → drivers.txt (overwrites)."""
        with open(self.filepath, "w") as f:
            for d in drivers:
                row = d.position.row
                col = d.position.col
                f.write(f"{d.id},{d.name},{d.phone},{d.car},{row},{col}\n")

    # ── display ───────────────────────────────

    def display(self, drivers):
        if not drivers:
            print("  No drivers on file.")
            return
        print(f"\n  {'ID':<6} {'Name':<12} {'Phone':<12} {'Car':<10} {'Position'}")
        print("  " + "-" * 50)
        for d in drivers:
            pos = f"({d.position.row},{d.position.col})"
            print(f"  {d.id:<6} {d.name:<12} {d.phone:<12} {d.car:<10} {pos}")


# ─────────────────────────────────────────────
# Admin
# ─────────────────────────────────────────────

class Admin:

    def __init__(self, filepath="drivers.txt"):
        self.file = DriversFile(filepath)

    # ── internal helpers ──────────────────────

    def _load(self):
        return self.file.load()

    def _save(self, drivers):
        self.file.save(drivers)

    def _find(self, drivers, driver_id):
        """Return (index, driver) or (None, None) if not found."""
        for i, d in enumerate(drivers):
            if d.id == driver_id:
                return i, d
        return None, None

    # ── public operations ─────────────────────

    def list_drivers(self):
        drivers = self._load()
        print("\n=== DRIVER LIST ===")
        self.file.display(drivers)

    def add_driver(self, id_, name, phone, car, row, col):
        """Add a new driver. Rejects duplicate IDs."""
        drivers = self._load()
        idx, _ = self._find(drivers, id_)
        if idx is not None:
            print(f"  [ERROR] Driver ID '{id_}' already exists.")
            return False
        drivers.append(Driver(id_, name, phone, car, row, col))
        self._save(drivers)
        print(f"  [OK] Driver '{name}' ({id_}) added.")
        return True

    def remove_driver(self, driver_id):
        """Remove a driver by ID."""
        drivers = self._load()
        idx, found = self._find(drivers, driver_id)
        if idx is None:
            print(f"  [ERROR] Driver ID '{driver_id}' not found.")
            return False
        drivers.pop(idx)
        self._save(drivers)
        print(f"  [OK] Driver '{found.name}' ({driver_id}) removed.")
        return True

    def edit_driver(self, driver_id, name=None, phone=None, car=None, row=None, col=None):
        """Edit one or more fields of an existing driver. Pass None to keep a field unchanged."""
        drivers = self._load()
        idx, found = self._find(drivers, driver_id)
        if idx is None:
            print(f"  [ERROR] Driver ID '{driver_id}' not found.")
            return False

        # guard: row and col must be non-negative integers if provided
        if row is not None and (not isinstance(row, int) or row < 0):
            print(f"  [ERROR] Row must be a non-negative integer, got '{row}'.")
            return False
        if col is not None and (not isinstance(col, int) or col < 0):
            print(f"  [ERROR] Col must be a non-negative integer, got '{col}'.")
            return False

        if name  is not None: found.name         = name
        if phone is not None: found.phone        = phone
        if car   is not None: found.car          = car
        if row   is not None: found.position.row = row
        if col   is not None: found.position.col = col

        drivers[idx] = found
        self._save(drivers)
        print(f"  [OK] Driver '{found.name}' ({driver_id}) updated.")
        return True
