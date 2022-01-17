from typing import Callable
from rich.table import Table


class UserInterface:
    """
    Utility class for common operations in menu.
    """

    def __init__(self, app) -> None:
        self.app = app

    def get_atoms(self, predicate: str, _filter: Callable | None = None):
        """
        Get all atoms with predicate name from arguments. If filter is
        provided, filter atoms using it.
        """
        atoms = []
        for atom in self.app.db.get_atoms(predicate):  # get atoms from solved database
            if _filter is not None and not _filter(atom):
                continue

            atoms.append(atom)

        return atoms

    def get_atoms_table(
        self, header: list, title: str, predicate: str, _filter: Callable | None = None
    ):
        """
        Return table containing atoms from provided predicate and filter them.
        """
        rows = []

        for atom in self.get_atoms(predicate, _filter):
            rows.append(atom.arguments)

        return self.get_table(header, rows, title)

    def get_menu(self, rows: list, title: str | None) -> Table:
        """
        Get menu table - used by Menu classes.
        """
        menu_table = self.get_table(["", "Akcia"], list(enumerate(rows, 1)), title)

        return menu_table

    def get_table(self, header: list, rows: list, title: str | None = None) -> Table:
        """
        Get printable table using provided arguments.
        """
        t = Table(*header, title=title)

        for row in rows:
            t.add_row(*list(map(str, row)))

        return t
