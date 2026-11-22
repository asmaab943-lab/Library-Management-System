import hashlib
import hmac

# Import database connection
from schema import get_connection

# Import functions
from auth import check_role
from books import add_book, search_book, display_books, delete_book
from borrowing import borrow_book, return_book


# Login
print("===== Library Management System =====")

username = input("Enter username: ")
password = input("Enter password: ")


# Get the saved (hashed) password from the database
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT password FROM users
    WHERE username = ?
""", (username,))

row = cursor.fetchone()
conn.close()


# Check the password: saved format is  salt$hash
login_ok = False

if row is not None:
    salt, saved_hash = row[0].split("$")

    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()

    login_ok = hmac.compare_digest(new_hash, saved_hash)


if login_ok:

    print("Login successful!")

    # Admin Menu
    if check_role(username, "admin"):

        while True:
            print("\n===== Admin Menu =====")
            print("1. Display Books")
            print("2. Search Book")
            print("3. Add Book")
            print("4. Delete Book")
            print("5. Logout")

            choice = input("Choose an option: ")

            if choice == "1":
                all_books = display_books()
                if not all_books:
                    print("No books available!")
                for book in all_books:
                    print(book)

            elif choice == "2":
                title = input("Enter book title: ")
                found = search_book(title)
                if not found:
                    print("Book not found!")
                for book in found:
                    print(book)

            elif choice == "3":
                title = input("Enter book title: ")
                author = input("Enter author name: ")
                category = input("Enter category: ")

                print(add_book(title, author, category))

            elif choice == "4":
                book_id = int(input("Enter book ID: "))
                print(delete_book(book_id))

            elif choice == "5":
                print("Logged out successfully!")
                break

            else:
                print("Invalid choice!")

    # User Menu
    elif check_role(username, "user"):

        while True:
            print("\n===== User Menu =====")
            print("1. Display Books")
            print("2. Search Book")
            print("3. Borrow Book")
            print("4. Return Book")
            print("5. Logout")

            choice = input("Choose an option: ")

            if choice == "1":
                all_books = display_books()
                if not all_books:
                    print("No books available!")
                for book in all_books:
                    print(book)

            elif choice == "2":
                title = input("Enter book title: ")
                found = search_book(title)
                if not found:
                    print("Book not found!")
                for book in found:
                    print(book)

            elif choice == "3":
                book_id = int(input("Enter book ID: "))
                print(borrow_book(username, book_id))

            elif choice == "4":
                book_id = int(input("Enter book ID: "))
                print(return_book(username, book_id))

            elif choice == "5":
                print("Logged out successfully!")
                break

            else:
                print("Invalid choice!")

else:
    print("Invalid username or password!")