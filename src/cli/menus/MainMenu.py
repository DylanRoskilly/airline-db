from cli.menus.Menu import Menu
from cli.menus.InsertMenu import InsertMenu
from cli.menus.UpdateMenu import UpdateMenu
from cli.menus.DeleteMenu import DeleteMenu
from cli.menus.SearchMenu import SearchMenu
from cli.menus.StatisticsMenu import StatisticsMenu

class MainMenu(Menu):
    def __init__(self, database: 'Database') -> None:   
        self.insert_menu = InsertMenu(database)
        self.update_menu = UpdateMenu(database)
        self.delete_menu = DeleteMenu(database)
        self.search_menu = SearchMenu(database)
        self.statistics_menu = StatisticsMenu(database)

    def print_menu(self) -> None:
        print("""
+------------------------------------+
|            MAIN MENU               |
+------------------------------------+
|   1. Insert data                   |
|   2. Update data                   |
|   3. Delete data                   |
|   4. Search data                   |
|   5. Get statistics                |
|   0. Quit                          |
+------------------------------------+
        """)

    def respond(self, option: str) -> None:
        match option:
            case "1":
                self.insert_menu.start()
            case "2":
                self.update_menu.start()
            case "3":
                self.delete_menu.start()
            case "4":
                self.search_menu.start()
            case "5":
                self.statistics_menu.start()



