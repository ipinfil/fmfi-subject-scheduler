from typing import Callable
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import String, Symbol


class Database:
    """
    Database class used to deal with clingo, load the base database to memory.
    """

    db_contents = None
    model: Model | None = None
    atoms: list[Symbol] | None = None
    shown_atoms = None
    bound_db = None
    is_bound: bool = False

    def __init__(self, db_path) -> None:
        """
        Solve clingo db and load it.
        """
        self.db_path = db_path
        self.load_database()

    def load_database(self):
        """
        Get database file content.
        """
        with open(self.db_path) as db:
            self.db_contents = db.read()

        # if it has a bound student's database, load it as well
        if self.bound_db is not None:
            self.bound_db.load_database()

    def get_database_contents(self):
        """
        Get database files content.
        """
        if self.db_contents is None:
            self.load_database()

        if self.bound_db is not None:
            self.db_contents += self.bound_db.get_database_contents()

        return self.db_contents

    def add_bound_database(self, path: str):
        """
        User has been logged in, load bound database.
        """
        self.bound_db = BoundDatabase(path, self)
        self.is_bound = True
        self.load_database()
        self.solve()

    def solve(self):
        """
        Solve ASP database using clingo, save atoms and shown atoms in properties.
        """
        control = Control()
        control.add("base", [], self.get_database_contents())
        control.ground([("base", [])])
        handle = control.solve(yield_=True)

        self.atoms, self.shown_atoms = list(handle.model().symbols(atoms=True)), list(
            handle.model().symbols(shown=True)
        )

    def get_atoms(self, predicates: str | list = None):
        """
        Get atoms with provided predicate/s.
        """
        if self.atoms is None:
            self.solve()

        if type(predicates) == str:
            predicates = [predicates]

        return (
            self.atoms
            if predicates is None
            else [symbol for symbol in self.atoms if symbol.name in predicates]
        )

    def extract_argument_from_atoms(self, predicate: str, arg_num: int) -> set:
        """
        Extract argument value from atoms with provided argument number.
        """

        if self.atoms is None:
            self.solve()

        args = []
        for atom in self.get_atoms(predicate):
            # subtract 1 - value in arg_num is not zero-based
            args.append(str(atom.arguments[arg_num - 1]))

        return set(args)

    def dict_from_atoms(self, predicate: str, key_arg: int, val_arg: int):
        """
        Create dict from atoms - key_arg is the key and val_arg value in the resulting dict.
        """
        if self.atoms is None:
            self.solve()

        result = {}
        for atom in self.get_atoms(predicate):
            args = atom.arguments
            result[str(args[key_arg - 1])] = str(args[val_arg - 1])

        return result


class BoundDatabase(Database):
    """
    Bound database used to load student's database.
    """

    main_db: Database | None = None

    def __init__(self, db_path, main_db: Database) -> None:
        """
        Save reference to the main db.
        """
        super().__init__(db_path)
        self.main_db = main_db

    def remove_atoms(
        self, predicates: str | list, save=False, filter: Callable | None = None
    ):
        """
        Remove atoms from the student's database.
        """
        if self.atoms is None:
            self.solve()

        if type(predicates) == str:
            predicates = [predicates]

        counter = len(self.atoms)
        tmp_atoms = []
        for atom in self.atoms:
            if atom.name in predicates and (filter is None or filter(atom)):
                continue
            tmp_atoms.append(atom)
        self.atoms = tmp_atoms
        counter -= len(self.atoms)

        # save only if wanted
        if save:
            self._save()

        return counter

    def add_atom(self, atom: str, save: bool = False) -> Symbol:
        """
        Add atom to student's database.
        """
        atom_symbol = String(atom)

        if self.atoms is None:
            self.solve()

        self.atoms.append(atom_symbol)

        if save:
            self._save()

        return atom_symbol

    def add_atoms(self, atoms: list[str], save: bool = False) -> list[Symbol]:
        """
        Add multiple atoms to student's database.
        """
        res = []

        for atom in atoms:
            res.append(self.add_atom(atom))

        if save:
            self._save()

        return res

    def _save(self):
        """
        Save database's content to the original file and load it immediately.
        """
        content = "\n".join(
            map(lambda atom: str(atom).strip('"').replace("\\", "") + ".", self.atoms)
        )

        with open(self.db_path, "w") as db:
            db.write(content)

        self.main_db.load_database()
        self.solve()
        self.main_db.solve()
