from database.Database import Database
from cli.menus.MainMenu import MainMenu

# initalise database
db = Database("airline")
db.connect()
db.create_tables()

# initalise main menu
main_menu = MainMenu(db)
main_menu.start()

# connection is closed when program ends so we dont have any opened connections not being used
db.cursor.close()
db.connection.close()