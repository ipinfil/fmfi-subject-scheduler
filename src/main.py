"""
Main file, application runs from here.
"""

from rich import print
from backend.db import Database
from backend.system import System
from frontend.ui import UserInterface
from config import db_path as config_db_path
from frontend.menu import MainMenu


class Application:
    """
    Application class containing all the necessary dependencies to run.
    """

    logged_in: bool = False

    def __init__(self, db_path):
        """
        Load all necessary dependencies.
        """
        self.db_path = db_path
        self.db = Database(db_path)
        self.ui = UserInterface(self)

    def start(self):
        """
        Start the application - run main menu.
        """
        print("[bold green]Zostavovač študijných plánov pre AIN[/bold green]")
        menu = MainMenu(self.ui)
        menu.run()

    def close(self):
        """
        Close the application.
        """
        exit()

    def logout(self):
        """
        Logout the user.
        """
        self.logged_in = False

        # load the database again without user bound database loaded
        self.db = Database(db_path)

    def login(self, name):
        """
        User login.
        """
        self.logged_in = True

        System.handle_login(name)

        # add bounded user database into the main database
        self.db.add_bound_database(System.get_students_db_path(name))


if __name__ == "__main__":
    db_path = config_db_path
    app = Application(db_path)

    try:
        app.start()
    except KeyboardInterrupt:
        app.close()
