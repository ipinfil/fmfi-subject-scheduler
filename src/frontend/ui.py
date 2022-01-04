from typing import Callable
from rich.table import Table

class UserInterface:
    def __init__(self, app) -> None:
        self.app = app

    def get_atoms(self, predicate, filter: Callable | None = None):
        atoms = []
        for atom in self.app.db.get_atoms(predicate):
            if filter is not None and not filter(atom):
                continue

            atoms.append(atom)

        return atoms

    def get_atoms_table(self, header, title, predicate, filter: Callable | None = None):
        rows = []

        for atom in self.get_atoms(predicate, filter):
            rows.append(atom.arguments)

        return self.get_table(header, rows, title)

    def get_menu(self, rows, title):
        menu_table = self.get_table(
            ['', 'Akcia'],
            enumerate(rows, 1),
            title
        )

        return menu_table

    def get_table(self, header: list, rows: list, title: str | None = None) -> Table:
        t = Table(*header, title=title)

        for row in rows:
            t.add_row(*list(map(str, row)))

        return t
