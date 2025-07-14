import sqlite3
import os
import random


def add_book(title: str, authorID: int, qty: int):
    # Adds a new book to the book table
    try:
        # Checks that an appropriate author exists in the author table
        cursor.execute("""SELECT * FROM author WHERE id=?""", (authorID,))
        result = len(cursor.fetchall())
        if result == 0:
            # Returns to the menu as no valid authorID
            print(f"Error: AuthorID {authorID} does not exist")
            return

        # Adds the new book to the book table
        cursor.execute(
            """INSERT INTO book(title,authorID,qty) VALUES(?,?,?);""",
            (title, authorID, qty),
        )
        db.commit()
        # Feedback for the user
        print(f"\n\nAdded {title} to the database.")
    except:
        print("Error: An Unexpected error occurred.")


def add_author(name: str, country: str):
    # Adds a new author to the author table, assuming the author ID
    # is random
    try:
        # Generates a random ID number that is not in use

        # Gets the highest number
        cursor.execute("SELECT max(id) FROM author")
        current_max_id = cursor.fetchone()[0]

        # Sets the highest possible ID value using the current amount of
        # digits in the hightest number
        max_num = 9
        # Adds 9 to the end of the number until the correct amount of
        # digits is reached
        for digit in range(len(str(current_max_id)) - 1):
            max_num *= 10
            max_num += 9
        # Checks that there is space in the current amount of digits to
        # generate a new ID
        cursor.execute("""SELECT id FROM author""")
        result = len(cursor.fetchall())
        if result == max_num:
            max_num *= 10
            max_num += 9

        # Generates a random number for the ID until one that isn't
        # used is found,without attempting to store all the
        # current ID's
        while True:
            new_id = random.randrange(1, max_num)
            cursor.execute("""SELECT id FROM author where id=?""", (new_id,))
            result = len(cursor.fetchall())
            if result == 0:
                break

        # Adds the author to the author table
        cursor.execute(
            """INSERT INTO author VALUES(?,?,?)""", (new_id, name, country)
        )
        db.commit()
        print(f"Added author {name} with an ID of {new_id}.")
    except:
        print("Error: An Unexpected error occurred.")


def update_book(id: int, option: str, new_value):
    # Updates a book's information given an ID,option and new value
    try:
        # Checks if the book ID given is valid
        cursor.execute("""SELECT * FROM book WHERE id=?""", (id,))
        result = len(cursor.fetchall())
        if result == 0:
            # Returns to menu as there is no matching book id
            print(f"Error: BookID {id} does not exist.")
            return

        # Allows the user to update a selection of values
        match option.lower():
            case "a":
                # Updates the Author
                cursor.execute("""UPDATE book SET authorID=?""", (new_value,))
                db.commit()
                print("Updates the book's AuthorID")
            case "t":
                # Updates the Title
                cursor.execute("""UPDATE book SET title=?""", (new_value,))
                db.commit()
                print("Updates the book's Title")
            case "q":
                # Updates the Quantity
                cursor.execute("""UPDATE book SET qty=?""", (new_value,))
                db.commit()
                print("Updates the book's Quantity")
            case _:
                # Error: No valid option was given
                print("Error: No Valid option was provided")
                return
    except IndexError:
        print(f"Error: There is no book with the value.")


def delete_book(id: int):
    # Removes a book entry from the book table
    try:
        # Checks if the book ID given is valid
        cursor.execute("""SELECT * FROM book WHERE id=?""", (id,))
        result = len(cursor.fetchall())
        if result == 0:
            # Returns to menu as there is no matching book ID
            print(f"Error: BookID {id} does not exist.")
            return
        # Removes the book entry from the table
        cursor.execute("""DELETE FROM book WHERE id=?""", (id,))
        db.commit()
        print(f"The book with an ID: {id} was deleted")
    except:
        print("Error: An Unexpected error occurred.")


def search_book(option: str, search_value):
    # Search's for a book's information given an option and search value
    try:
        match str(option.lower()):

            case "a":
                # Search's with Author
                cursor.execute(
                    """SELECT * FROM book WHERE authorID=?""", (search_value,)
                )
            case "t":
                # Search's with Title
                cursor.execute(
                    """SELECT * FROM book WHERE title=?""", (search_value,)
                )
            case "b":
                # Search's with ID
                cursor.execute(
                    """SELECT * FROM book WHERE id=?""", (search_value,)
                )
            case _:
                # Error: No valid option was given
                print("Error: No Valid option was provided.")
                return

        # Generates an output from the search type
        output_list = cursor.fetchall()
        book_id, title, author_id, qty = zip(*output_list)

        # Puts the output in a readable manner
        output_string = "\nSearch Results:\n"
        for index in range(len(output_list)):
            output_string += "--------------------------------\n"
            output_string += f"Book ID: {book_id[index]}\n"
            output_string += f"Title: {title[index]}\n"
            output_string += f"Author ID: {author_id[index]}\n"
            output_string += f"Quantity: {qty[index]}\n"
        print(output_string)
    except IndexError:
        print(f"Error: There is no book with the {search_value} value.")


def view_details():
    # Gets the details of every book with it's author
    cursor.execute(
        """SELECT b.title,a.name,a.country FROM book AS b INNER JOIN
        author AS a ON b.authorID = a.ID"""
    )
    output_list = cursor.fetchall()

    # Generates the output
    title, name, country = zip(*output_list)
    # Puts the output in a readable manner
    output_string = "\nDetails\n"
    for index in range(len(output_list)):
        output_string += f"--------------------------------\n"
        output_string += f"Title: {title[index]}\n"
        output_string += f"Author's Name: {name[index]}\n"
        output_string += f"Author's Country: {country[index]}\n"
    print(output_string)


def backup_db():
    # Backs up the tables

    # Checks if the backup tables exist
    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND
        name='backup_book';"""
    )
    # Backup tables don't exist
    if len(cursor.fetchall()) == 0:
        create_backup_tables()

    # Empties the back up tables and copies the data from the
    # regular tables
    cursor.executescript(
        """
DELETE FROM backup_book;
DELETE FROM backup_author;
INSERT INTO backup_book SELECT * FROM book;
INSERT INTO backup_author SELECT * FROM author;
"""
    )
    db.commit()
    print("The database was backed up")


def restore_backup_db():
    # Copies the data from the backup tables to the regular tables
    try:
        # Checks if there is a backup of the tables
        cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'AND
            name='backup_book';"""
        )

        # There is a back up
        if len(cursor.fetchall()) == 1:
            # Empties the regular tables and copies the data from the
            # backup tables
            cursor.executescript(
                """
DELETE FROM book;
DELETE FROM author;
INSERT INTO book SELECT * FROM backup_book;
INSERT INTO author SELECT * FROM backup_author;
    """
            )
            db.commit()
            print("Database restored to last backup")
        else:
            # Error: There is no back up
            print("Error: No backups Exist")

    except:
        print("Error: An Unexpected error occurred.")


def create_backup_tables():
    # Creates the empty backup tables, structurally identical to the
    # normal tables
    cursor.executescript(
        """
CREATE TABLE backup_book(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,
                            authorID INTEGER,qty INTEGER);
CREATE TABLE backup_author(id INTEGER PRIMARY KEY,name TEXT,country TEXT);
"""
    )


def db_create():
    # Creates the database as well as the basic tables' structure and
    # populates the tables
    db = db_connect()
    cursor = db.cursor()
    cursor.executescript(
        """
CREATE TABLE book(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,
                    authorID INTEGER,qty INTEGER);
INSERT INTO book VALUES(3001,'A Tale of Two Cities',1290,30),
                   (3002,"Harry Potter and the Philosopher's Stone",8937,40),
                   (3003,'The Lion, the Witch and the Wardrobe',2356,25),
                   (3004,'The Lord of the Rings',6380,37),
                   (3005,"Alice's Adventures in Wonderland",5620,12);
CREATE TABLE author(id INTEGER PRIMARY KEY,name TEXT,country TEXT);
INSERT INTO author VALUES(1290,"Charles Dickens","England"),
               (8937,"J.K. Rowling","England"),
                (2356,"C.S. Lewis","Ireland"),
               (6380,"J.R.R. Tolkien","South Africa"),
               (5620,"Lewis Carroll","England");        

"""
    )
    db.commit()
    print("Made Database")


def db_delete():
    # Deletes the entire database
    os.remove("ebookstore")
    print("Deleted Entire database")


def db_connect():
    # Connects/Creates the database
    return sqlite3.connect("ebookstore")


db = db_connect()
cursor = db.cursor()
# Main application loop
print("Welcome to INSERT_NAME's Books")
while True:
    try:
        # Main menu option
        option = int(
            input(
                """
Please select an option to continue:
1. Enter new book
2. Enter new author
3. Update book information
4. Delete book entry
5. Search for book
6. View details of all books
7. Backup management
0. Exit
"""
            )
        )
        # Checks if the user option is valid
        match option:
            case 0:
                # Exit
                print("Exiting Application")
                break

            case 1:
                # Add book
                print("Selected: Enter new book.\nPlease input:")
                title = input("Book title:\n")
                author_id = int(input("Book author ID:\n"))
                qty = int(input("Amount of books:\n"))
                add_book(title, author_id, qty)

            case 2:
                # Add Author
                print("Selected: Enter new author.\nPlease input:")
                name = input("Author's name:\n")
                country = input("Author's country:\n")
                add_author(name, country)

            case 3:
                # Update book
                print("Selected: Update book information.\nPlease input:")
                book_id = int(input("Book ID:\n"))
                choice = input(
                    """
Information to update:
a - AuthorID
t - Title
q - Quantity\n
"""
                )
                new_value = input("New value for selected option:\n")
                update_book(book_id, choice.lower(), new_value)

            case 4:
                # Delete book
                print("Selected: Delete book.\nPlease input:")
                book_id = int(input("Book id:\n"))
                delete_book(book_id)

            case 5:
                # Search for book
                print("Selected: Search book.\nPlease input:")
                choice = input(
                    """
Search type:
a - AuthorID
t - Title
b - book ID\n
"""
                )
                search_value = input("Search Value:\n")
                search_book(choice, search_value)

            case 6:
                # View all books
                print("Selected: View details of all book.")
                view_details()

            case 7:
                # Backup management
                print("Selected: Backup management.\nPlease input:")
                choice = input(
                    """
Backup management option:
b - Backup database
r - Restore database to previous backup\n
"""
                )
                match choice.lower():
                    case "b":
                        backup_db()
                    case "r":
                        restore_backup_db()
                    case _:
                        print("Error: No valid option")

            case _:
                # No Valid option
                print("Error: No valid option.Please enter a number")
    # Error parsing
    except ValueError:
        print("Error: Please input a number")

    except KeyboardInterrupt:
        print("Exiting Application")
        break
