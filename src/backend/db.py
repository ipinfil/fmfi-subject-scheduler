from typing import Callable
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import String, Symbol

class Database:
    db_contents = None
    model: Model | None = None
    atoms: list[Symbol] | None = None
    shown_atoms = None
    bound_db = None
    is_bound = False

    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.load_database()

    def load_database(self):
        with open(self.db_path) as db:
            self.db_contents = db.read()

        if self.bound_db is not None:
            self.bound_db.load_database()

    def get_database_contents(self):
        if self.db_contents is None:
            self.load_database()

        if self.bound_db is not None:
            self.db_contents += self.bound_db.get_database_contents()

        return self.db_contents

    def add_bound_database(self, path):
        self.bound_db = BoundDatabase(path, self)
        self.is_bound = True
        self.load_database()
        self.solve()

    def solve(self):
        control = Control()
        control.add("base", [], self.get_database_contents())
        control.ground([("base", [])])
        handle = control.solve(yield_=True)

        self.atoms, self.shown_atoms = list(handle.model().symbols(atoms=True)), list(handle.model().symbols(shown=True))

    def get_atoms(self, predicates: str | list = None):
        if self.atoms is None:
            self.solve()

        if type(predicates) == str:
            predicates = [predicates]

        return self.atoms if predicates is None else [symbol for symbol in self.atoms if symbol.name in predicates]

    def extract_argument_from_atoms(self, predicate: str, arg_num: int) -> set:
        if self.atoms is None:
            self.solve()

        args = []
        for atom in self.get_atoms(predicate):
            args.append(str(atom.arguments[arg_num - 1]))

        return set(args)

    def dict_from_atoms(self, predicate: str, key_arg: int, val_arg: int):
        if self.atoms is None:
            self.solve()

        result = {}
        for atom in self.get_atoms(predicate):
            args = atom.arguments
            result[str(args[key_arg - 1])] = str(args[val_arg - 1])

        return result

class BoundDatabase(Database):
    main_db: Database | None = None

    def __init__(self, db_path, main_db: Database) -> None:
        super().__init__(db_path)
        self.main_db = main_db

    def remove_atoms(self, predicates: str | list, save=False, filter: Callable | None=None):
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

        if save:
            self._save()

        return counter

    def add_atom(self, atom: str, save: bool=False) -> Symbol:
        atom_symbol = String(atom)

        if self.atoms is None:
            self.solve()

        self.atoms.append(atom_symbol)

        if save:
            self._save()

        return atom_symbol

    def add_atoms(self, atoms: list[str], save: bool=False) -> list[Symbol]:
        res = []

        for atom in atoms:
            res.append(self.add_atom(atom))

        if save:
            self._save()

        return res

    def _save(self):
        content = '\n'.join(map(
            lambda atom: str(atom).strip('"').replace("\\", "") + '.'
            , self.atoms))

        with open(self.db_path, 'w') as db:
            db.write(content)

        self.main_db.load_database()
        self.solve()
        self.main_db.solve()

