

from admin import Admin, DriversFile
from models import Passenger, RideRequest
from grid import Grid
from system import RideMatchingSystem

def input_int(prompt):
    """Keep asking until the user enters a valid integer."""
    while True:
        value = input(prompt).strip()
        if value.lstrip('-').isdigit():
            return int(value)
        print("  Please enter a number.")


def input_positive_int(prompt):
    """Keep asking until the user enters a positive integer (> 0)."""
    while True:
        value = input_int(prompt)
        if value > 0:
            return value
        print("  Value must be greater than 0.")


def input_str(prompt):
    """Ask for a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty.")


# ─────────────────────────────────────────────
# Admin sub-menu
# ─────────────────────────────────────────────

def admin_menu(admin):

    while True:
        print("\n--- Admin Panel ---")
        print("  1. List drivers")
        print("  2. Add driver")
        print("  3. Remove driver")
        print("  4. Edit driver")
        print("  5. Back")

        choice = input("  Choice: ").strip()

        if choice == "1":
            admin.list_drivers()

        elif choice == "2":
            print("\n  -- Add Driver --")
            id_   = input_str("  ID    : ")
            name  = input_str("  Name  : ")
            phone = input_str("  Phone : ")
            car   = input_str("  Car   : ")
            row   = input_int("  Row   : ")
            col   = input_int("  Col   : ")
            # guard: negative position rejected before Driver() is created
            if row < 0 or col < 0:
                print("  [ERROR] Row and col must be non-negative.")
            else:
                admin.add_driver(id_, name, phone, car, row, col)

        elif choice == "3":
            print("\n  -- Remove Driver --")
            admin.list_drivers()
            driver_id = input_str("  Driver ID to remove: ")
            admin.remove_driver(driver_id)

        elif choice == "4":
            print("\n  -- Edit Driver --")
            admin.list_drivers()
            driver_id = input_str("  Driver ID to edit: ")
            print("  (press Enter to keep current value)")

            name  = input("  New name  : ").strip() or None
            phone = input("  New phone : ").strip() or None
            car   = input("  New car   : ").strip() or None

            row_in = input("  New row   : ").strip()
            col_in = input("  New col   : ").strip()

            # convert only if provided; validate before passing
            row, col = None, None
            if row_in:
                if row_in.lstrip('-').isdigit() and int(row_in) >= 0:
                    row = int(row_in)
                else:
                    print("  [!] Invalid row — keeping current value.")
            if col_in:
                if col_in.lstrip('-').isdigit() and int(col_in) >= 0:
                    col = int(col_in)
                else:
                    print("  [!] Invalid col — keeping current value.")

            admin.edit_driver(driver_id, name, phone, car, row, col)

        elif choice == "5":
            break

        else:
            print("  Invalid choice.")


# ─────────────────────────────────────────────
# Run ride-matching system
# ─────────────────────────────────────────────

def run_system(admin):

    # load drivers from file
    drivers = DriversFile().load()
    if not drivers:
        print("\n  [!] No drivers in file. Add drivers from the Admin panel first.")
        return

    print(f"\n  Loaded {len(drivers)} driver(s) from file.")

    # set up grid first so we can validate driver positions
    grid_rows = input_positive_int("\n  Grid rows : ")
    grid_cols = input_positive_int("  Grid cols : ")
    grid = Grid(grid_rows, grid_cols)

    # guard: drop drivers whose saved position is outside this grid
    valid_drivers = []
    for d in drivers:
        if grid.isValid(d.position.row, d.position.col):
            grid.placeDriver(d)
            valid_drivers.append(d)
        else:
            print(f"  [!] Driver '{d.name}' ({d.id}) position ({d.position.row},{d.position.col}) "
                  f"is outside the {grid_rows}x{grid_cols} grid — skipped.")

    if not valid_drivers:
        print("  [!] No valid drivers for this grid size. Aborting.")
        return

    # collect ride requests
    requests = []
    print("\n  Enter ride requests (type 'done' when finished):")

    req_id = 1
    while True:
        print(f"\n  Request #{req_id}")
        stop = input("  Press Enter to add, or type 'done' to finish: ").strip().lower()
        if stop == "done":
            break

        pickup_row = input_int("  Pickup row  : ")
        pickup_col = input_int("  Pickup col  : ")
        dest_row   = input_int("  Dest row    : ")
        dest_col   = input_int("  Dest col    : ")

        # guard: pickup and destination must be inside the grid
        if not grid.isValid(pickup_row, pickup_col):
            print(f"  [!] Pickup ({pickup_row},{pickup_col}) is outside the grid — request skipped.")
            continue
        if not grid.isValid(dest_row, dest_col):
            print(f"  [!] Destination ({dest_row},{dest_col}) is outside the grid — request skipped.")
            continue
        if pickup_row == dest_row and pickup_col == dest_col:
            print("  [!] Pickup and destination are the same cell — request skipped.")
            continue

        requests.append(RideRequest(req_id, Passenger(pickup_row, pickup_col, dest_row, dest_col)))
        req_id += 1

    if not requests:
        print("  No valid requests entered.")
        return

    # run the system
    system = RideMatchingSystem(grid, valid_drivers, requests)
    system.run()




def main():

    admin = Admin()

    print("=" * 40)
    print("   Ride Matching System")
    print("=" * 40)

    while True:
        print("\n  1. Admin panel")
        print("  2. Run ride system")
        print("  3. Exit")

        choice = input("  Choice: ").strip()

        if choice == "1":
            admin_menu(admin)

        elif choice == "2":
            run_system(admin)

        elif choice == "3":
            print("  Goodbye.")
            break

        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
