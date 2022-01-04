from rich import print
from backend.db import Database
from backend.system import System
from frontend.ui import UserInterface
from config import db_path as config_db_path
from frontend.menu import MainMenu

class Application:
    logged_in = False

    def __init__(self, db_path):
        self.db_path = db_path
        self.db = Database(db_path)
        self.ui = UserInterface(self)

    def start(self):
        print('[bold green]Zostavovač študijných plánov pre AIN[/bold green]')
        menu = MainMenu(self.ui)
        menu.run()

    def close(self):
        exit()

    def logout(self):
        self.logged_in = False
        self.db = Database(db_path)

    def login(self, name):
        self.logged_in = True

        System.handle_login(name)
        self.db.add_bound_database(System.get_students_db_path(name))


if __name__ == "__main__":
    db_path = config_db_path
    app = Application(db_path)

    try:
        app.start()
    except KeyboardInterrupt:
        app.close()