from abc import ABCMeta, abstractmethod
from rich import print
from config import DEBUG
from frontend.ui import UserInterface


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
