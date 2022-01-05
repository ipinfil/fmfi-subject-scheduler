from abc import ABCMeta, abstractmethod
from rich import print
from typing import Callable, Type
from config import DEBUG
from backend.db import BoundDatabase
from frontend.ui import UserInterface
from backend.system import PredicateManager


class Menu(metaclass=ABCMeta):
    """
    Abstract class defining generally used methods in menu classes.
    """

    title = None
    menu_items = None
    handlers = None
    ui = None
    is_running = False
    menu_table = None

    def __init__(self, ui: UserInterface):
        """
        Save UserInterface reference, create menu items.
        """
        self.ui = ui

        self._create_menu()

        if self.title is None or self.menu_items is None or self.handlers is None:
            raise NotImplementedError()

    def run(self):
        """
        Run the menu in cycle.
        """
        if self.menu_table is None:
            self._get_menu_table()

        self.is_running = True
        while self.is_running:
            print(self.menu_table)
            self._handle_action()

    def _get_menu_table(self):
        """
        Get menu table for printing.
        """
        self.menu_table = self.ui.get_menu(self.menu_items, self.title)

    def _handle_action(self):
        """
        Handle user action.
        """
        print("[bold green]Zadajte akciu: [/bold green]", end="")
        action = int(input().strip()) - 1
        try:
            return self.handlers[action]()
        except IndexError as e:
            if DEBUG:
                raise e
            print(
                "[bold red]Takáto akcia neexistuje. Zadajte voľbu ešte raz.[/bold red]"
            )
            return self._handle_action()

    @abstractmethod
    def _create_menu(self):
        """
        Define menu items and handlers.
        """
        pass

    @abstractmethod
    def _close(self):
        """
        Close the menu.
        """
        pass


class MainMenu(Menu):
    """
    MainMenu class.
    """

    title = "Hlavné menu"

    def _create_menu(self):
        self.menu_items = [
            "Prihlásenie" if not self.ui.app.logged_in else "Odhlásenie",
            "Zobraziť dáta",
        ]

        self.handlers = [
            self._login if not self.ui.app.logged_in else self._logout,
            self._run_menu(ShowDataMenu),
        ]

        if self.ui.app.logged_in:
            self.menu_items += ["Správa rozvrhu", "Správa preferencií"]
            self.handlers += [
                self._run_menu(SubjectsMenu),
                self._run_menu(PreferencesMenu),
            ]

        self.menu_items.append("Vypnúť")
        self.handlers.append(self._close)

    def _login(self):
        """
        Login handler.
        """
        print()
        print("[bold green]Zadajte svoje univerzitné meno: [/bold green]", end="")
        name = input().strip()
        self.ui.app.login(name)
        self._create_menu()
        self._get_menu_table()

        print("[bold blue]Boli ste prihlásený.[/bold blue]")
        print()

    def _logout(self):
        """
        Logout handler.
        """
        print()

        self.ui.app.logout()
        self._create_menu()
        self._get_menu_table()

        print("[bold blue]Boli ste odhlásený.[/bold blue]")
        print()

    def _close(self):
        self.ui.app.close()

    def _run_menu(self, menu_class: Type[Menu]) -> Callable:
        """
        Run submenus.
        """
        menu = menu_class(self.ui)
        return menu.run


class Submenu(Menu):
    """
    Base submenu class, concrete submenus inherit from this one.
    """

    def _create_menu(self):
        # automatically include redirect to the main menu
        if (
            self.menu_items is not None
            and isinstance(self.menu_items, list)
            and self.handlers is not None
            and isinstance(self.handlers, list)
            and len(self.handlers) > 0
        ):
            if self.menu_items[0] != MainMenu.title:
                self.menu_items.insert(0, MainMenu.title)

            if len(self.handlers) != len(self.menu_items):
                self.handlers.insert(0, self._close)

        return super()._create_menu()

    def _visualize_predicate(self, predicate: int, filter: Callable | None = None):
        """
        Print table containing atoms with provided predicate.
        """

        def do_visualize():
            table = self.ui.get_atoms_table(
                PredicateManager.get_predicate_argument_titles(predicate),
                PredicateManager.get_predicate_title(predicate),
                PredicateManager.get_predicate_name(predicate),
                filter,
            )
            print(table)

        return (
            do_visualize  # returning function, since the handlers need to be callable
        )

    def _visualize_predicates(self, predicates: list[int]):
        """
        Visualize multiple predicates.
        """

        def do_visualize():
            for predicate in predicates:
                self._visualize_predicate(predicate)()

        return do_visualize

    def _bool_answer_input(self, question, default=True):
        """
        Handlers user input for bool type of questions.
        """
        answer_ok = False
        yes, no = ("Y" if default else "y"), ("n" if default else "N")

        while not answer_ok:
            print(f"[bold green]{question}[/bold green] [{yes}/{no}]", end="")
            user_input = input().lower()

            if user_input in ["", "y", "n"]:
                answer_ok = True
            else:
                print(
                    f"[bold red]Vaša voľba nie je správna. Zopakujte odpoveď, prosím.[/bold red]"
                )

        # for empty input, return default
        return True if user_input == "y" else (False if user_input == "n" else default)

    def _user_answer_input(self, question, allowed_values=None):
        """
        Handles user input for general type of questions.
        """
        answer_ok = False

        while not answer_ok:
            print(f"[bold green]{question}[/bold green] ", end="")
            user_input = input().lower().strip()

            if allowed_values is not None and user_input not in allowed_values:
                print(
                    f"[bold red]Vaša voľba nie je správna. Zopakujte odpoveď, prosím.[/bold red]"
                )
            else:
                answer_ok = True

        return user_input

    def _close(self):
        self.is_running = False


class ShowDataMenu(Submenu):
    title = "Zobraziť dáta"
    menu_items = [
        "Zobraziť predmety",
        "Zobraziť učiteľov",
        "Zobraziť technológie",
        "Zobraziť tématické okruhy",
    ]

    def _create_menu(self):
        self.handlers = [
            self._visualize_predicate(PredicateManager.PREDMET),
            self._visualize_predicate(PredicateManager.UCITEL),
            self._visualize_predicate(PredicateManager.TECHNOLOGIA),
            self._visualize_predicate(PredicateManager.TEMATICKY_OKRUH),
        ]

        return super()._create_menu()


class PreferencesMenu(Submenu):
    title = "Správa preferencií"
    menu_items = [
        "Zobraziť preferencie",
        "Zmeniť žiadané technológie",
        "Zmeniť žiadané tématické okruhy",
        "Zmeniť učiteľov",
    ]

    def _create_menu(self):
        self.handlers = [
            self._visualize_predicates(
                [
                    PredicateManager.STUDENT_TECHNOLOGIA,
                    PredicateManager.STUDENT_TEMATICKY_OKRUH,
                    PredicateManager.STUDENT_VYLUCENY_UCITEL,
                ]
            ),
            self._change_technology,
            self._change_thematic_area,  # ??? :D preklad za vsetky drobne
            self._change_teacher,
        ]
        return super()._create_menu()

    def _change_technology(self):
        self._change_preference(
            PredicateManager.TECHNOLOGIA, PredicateManager.STUDENT_TECHNOLOGIA
        )

    def _change_thematic_area(self):
        self._change_preference(
            PredicateManager.TEMATICKY_OKRUH, PredicateManager.STUDENT_TEMATICKY_OKRUH
        )

    def _change_teacher(self):
        self._change_preference(
            PredicateManager.UCITEL, PredicateManager.STUDENT_VYLUCENY_UCITEL
        )

    def _change_preference(self, predicate: int, bound_predicate: int):
        """
        Change preference of certain type provided in predicate argument.
        Predicate is the base database predicate, bound_predicate is the predicate
        used for saving user preferences.
        """
        bound_predicate_details = PredicateManager.PREDICATES[bound_predicate]
        predicate_details = PredicateManager.PREDICATES[predicate]

        print(
            f'[bold red]Zmena atómov typu - {bound_predicate_details["title"]}[/bold red]'
        )
        print(f'Existujúce atómy typu - {bound_predicate_details["title"]}:')
        self._visualize_predicate(bound_predicate)()

        user_input = self._bool_answer_input(
            f'Vymazať všetky existujúce atómy typu - {bound_predicate_details["title"]}?'
        )
        bound_db: BoundDatabase = self.ui.app.db.bound_db

        if user_input:
            count = bound_db.remove_atoms(bound_predicate_details["name"], True)
            print(
                f'[green]Bolo vymazaných {count} atómov typu - {bound_predicate_details["title"]}.[/green]'
            )

        user_input = self._bool_answer_input(
            f'Zobraziť existujúce atómy typu - {predicate_details["title"]}?'
        )
        if user_input:
            self._visualize_predicate(predicate)()

        user_input = self._bool_answer_input(
            f'Chcete pridať nové atómy typu - {bound_predicate_details["title"]}?'
        )
        if user_input:
            answer_ok = False

            # control answers with existing ids
            existing_ids = self.ui.app.db.extract_argument_from_atoms(
                predicate_details["name"], 1
            )

            while not answer_ok:
                print(
                    "[bold green]Zadajte ID atómov oddelené čiarkou: [/bold green]",
                    end="",
                )
                user_input = list(
                    map(lambda string: string.strip(), input().split(","))
                )

                answer_ok = True

                for id in user_input:
                    if id not in existing_ids:
                        print(
                            f'[bold red]Atóm typu {predicate_details["title"]} s id "{id}" neexistuje![/bold red]'
                        )
                        answer_ok = False
                        break

            symbols = bound_db.add_atoms(
                [f'{bound_predicate_details["name"]}({id})' for id in user_input], True
            )
            print(
                f'[green]Bolo pridaných {len(symbols)} atómov typu {bound_predicate_details["title"]}.[/green]'
            )


class SubjectsMenu(Submenu):
    title = "Správa rozvrhu"
    menu_items = ["Zobraziť zapísané predmety", "Správa študijného rozvrhu"]

    def _create_menu(self):
        self.handlers = [
            self._visualize_predicate(PredicateManager.STUDENT_ZAPISANY_PREDMET),
            self._schedule_administration,
        ]
        return super()._create_menu()

    def _statistics(self):
        """
        Print statistics including counts and sums of subjects and credits in student's study schedule.
        """
        print("Štatistika štúdia:")

        semester_mapping = {
            "z": "zimný",
            "l": "letný",
        }

        rows = []

        # get statistics for each semester of each year
        for year in ["1", "2", "3"]:
            for semester in semester_mapping:
                # filter atoms from db according to actual semester and year
                credits_count = str(
                    self.ui.get_atoms(
                        "pocet_kreditov_zapisane_semester_rok",
                        lambda atom: str(atom.arguments[1]) == semester
                        and str(atom.arguments[2]) == year,
                    )[0].arguments[0]
                )
                subjects_count = str(
                    self.ui.get_atoms(
                        "pocet_predmetov_zapisane_semester_rok",
                        lambda atom: str(atom.arguments[1]) == semester
                        and str(atom.arguments[2]) == year,
                    )[0].arguments[0]
                )

                rows.append([year, semester, credits_count, subjects_count])

        # credits and subjects count for the whole student's study schedule

        subjects_count = str(
            self.ui.get_atoms("pocet_predmetov_zapisane")[0].arguments[0]
        )
        credits_count = int(
            str(self.ui.get_atoms("pocet_kreditov_zapisane")[0].arguments[0])
        )

        if credits_count < 180:  # not enough credits warning
            credits_count = f"[bold red]{credits_count}[/bold red]"
            print(
                "[bold red]Nemáte dostatok kreditov na absolvovanie bakalárskeho programu AIN.[/bold red]"
            )

        rows.append(["", "", credits_count, subjects_count])
        table = self.ui.get_table(
            [
                "Rok štúdia",
                "Semester",
                "Počet kreditov zapísaných predmetov",
                "Počet zapísaných predmetov",
            ],
            rows,
        )
        print(table)

    def _prerequisites(self):
        """
        Display not enrolled prerequisites for enrolled subjects.
        """
        missing_prerequisites = self.ui.get_atoms(
            PredicateManager.get_predicate_name(
                PredicateManager.CHYBA_ZAPISANA_PREREKVIZITA
            )
        )

        if len(missing_prerequisites) == 0:
            return

        print(
            "[bold red]Zapísali ste si predmety, ktorých prerekvizity nemáte zapísané![/bold red]"
        )
        self._visualize_predicate(PredicateManager.CHYBA_ZAPISANA_PREREKVIZITA)()

    def _schedule_administration(self):
        """
        Schedule administration - show enrolled subjects, show recommended subjects, remove, add new enrolled subjects.
        Shows recommended subjects according to student's preferences.
        """
        print("[bold red]Správa študijného rozvrhu[/bold red]")
        self._statistics()
        self._prerequisites()

        # year and semester choice
        year = self._user_answer_input(
            "Zadajte rok štúdia, ktorý chcete spracovať: [1, 2, 3]", ["1", "2", "3"]
        )
        semester_choices = [
            PredicateManager.WINTER_SEMESTER_CONST,
            PredicateManager.SUMMER_SEMESTER_CONST,
        ]
        semester = self._user_answer_input(
            f"Zadajte rok štúdia, ktorý chcete spracovať: {semester_choices}",
            semester_choices,
        )

        semester_verbose = (
            "letnom" if semester == PredicateManager.SUMMER_SEMESTER_CONST else "zimnom"
        )
        show_enrolled_subjects = self._bool_answer_input(
            f"Zobraziť zapísané predmety v {semester_verbose} semestri {year}. ročníka?"
        )

        if show_enrolled_subjects:
            self._visualize_predicate(
                PredicateManager.STUDENT_ZAPISANY_PREDMET,
                lambda symbol: str(symbol.arguments[3]) == semester
                and str(symbol.arguments[2]) == year,
            )()

        show_recommended_subjects = self._bool_answer_input(
            f"Zobraziť odporučené predmety v {semester_verbose} semestri podľa navolených preferencií?"
        )
        if show_recommended_subjects:
            self._visualize_predicate(
                PredicateManager.ODPORUCENY_PREDMET,
                lambda symbol: str(symbol.arguments[2]) == semester,
            )()

        bound_db: BoundDatabase = self.ui.app.db.bound_db

        remove_enrolled_subjects = self._bool_answer_input(
            "Odstrániť niektoré zapísané predmety?"
        )
        if remove_enrolled_subjects:
            answer_ok = False
            existing_ids = self.ui.app.db.extract_argument_from_atoms(
                PredicateManager.get_predicate_name(
                    PredicateManager.STUDENT_ZAPISANY_PREDMET
                ),
                1,
            )

            # show enrolled subjects in this year an semester
            self._visualize_predicate(
                PredicateManager.STUDENT_ZAPISANY_PREDMET,
                lambda symbol: str(symbol.arguments[3]) == semester
                and str(symbol.arguments[2]) == year,
            )()

            while not answer_ok:
                print(
                    "[bold green]Zadajte ID predmetov oddelené čiarkou: [/bold green]",
                    end="",
                )
                user_input = list(
                    map(lambda string: string.strip(), input().split(","))
                )
                answer_ok = True

                for id in user_input:
                    if id not in existing_ids:
                        print(f'[bold red]Predmet s id "{id}" neexistuje![/bold red]')
                        answer_ok = False
                        break

            count = bound_db.remove_atoms(
                PredicateManager.get_predicate_name(
                    PredicateManager.STUDENT_ZAPISANY_PREDMET
                ),
                True,
                lambda atom: str(atom.arguments[0]) in user_input,
            )
            print(f"[green]Bolo odstránených {count} zapísaných predmetov.[/green]")

        add_enrolled_subjects = self._bool_answer_input("Zapísať predmety?")
        if add_enrolled_subjects:
            answer_ok = False

            # control user input with existing ids of not enrolled subjects
            existing_ids = self.ui.app.db.extract_argument_from_atoms(
                PredicateManager.get_predicate_name(
                    PredicateManager.NEZAPISANY_PREDMET
                ),
                1,
            )

            # show not enrolled subjects
            self._visualize_predicate(
                PredicateManager.NEZAPISANY_PREDMET,
                lambda symbol: str(symbol.arguments[2]) == semester,
            )()

            # show recommended subjects in this year an semester
            self._visualize_predicate(
                PredicateManager.ODPORUCENY_PREDMET,
                lambda symbol: str(symbol.arguments[2]) == semester,
            )()

            while not answer_ok:
                print(
                    "[bold green]Zadajte ID predmetov oddelené čiarkou: [/bold green]",
                    end="",
                )
                user_input = list(
                    map(lambda string: string.strip(), input().split(","))
                )
                answer_ok = True

                for id in user_input:
                    if id not in existing_ids:
                        print(
                            f'[bold red]Predmet s id "{id}" neexistuje alebo už je zapísaný![/bold red]'
                        )
                        answer_ok = False
                        break

            # get subject names to include in enrolled subject atom
            subject_names = self.ui.app.db.dict_from_atoms(
                PredicateManager.get_predicate_name(PredicateManager.PREDMET), 1, 2
            )

            # add new enrolled subjects
            atoms = bound_db.add_atoms(
                [
                    f"{PredicateManager.get_predicate_name(PredicateManager.STUDENT_ZAPISANY_PREDMET)}({subject_id}, {subject_names[subject_id]}, {year}, {semester})"
                    for subject_id in user_input
                ],
                True,
            )
            print(f"[green]Bolo pridaných {len(atoms)} zapísaných predmetov.[/green]")
