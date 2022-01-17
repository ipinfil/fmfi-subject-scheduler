from typing import Type, Callable
from rich import print
from .menu import Menu
from .submenu import ShowDataMenu, SubjectsMenu, PreferencesMenu

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
