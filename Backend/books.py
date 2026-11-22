from schema import get_connection


# Add a new book (the database creates the ID automatically)
def add_book(title, author, category):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if the book already exists
    cursor.execute("""
        SELECT book_id FROM books
        WHERE title = ? AND author = ?
    """, (title, author))

    if cursor.fetchone():
        conn.close()
        return "Book already exists!"

    cursor.execute("""
        INSERT INTO books (title, author, category)
        VALUES (?, ?, ?)
    """, (title, author, category))

    conn.commit()
    conn.close()

    return "Book added successfully!"


# Search for books (returns a list of all matches)
def search_book(title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT book_id, title, author, category, available
        FROM books
        WHERE title LIKE ?
    """, ('%' + title + '%',))

    results = cursor.fetchall()
    conn.close()

    books_list = []

    for book in results:
        books_list.append({
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "category": book[3],
            "available": bool(book[4])
        })

    return books_list


# Display all books (returns the list)
def display_books():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT book_id, title, author, category, available
        FROM books
    """)

    results = cursor.fetchall()
    conn.close()

    books_list = []

    for book in results:
        books_list.append({
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "category": book[3],
            "available": bool(book[4])
        })

    return books_list


# Delete a book (not allowed if borrowed or has borrowing history)
def delete_book(book_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT available FROM books
        WHERE book_id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if book is None:
        conn.close()
        return "Book not found!"

    if book[0] == 0:
        conn.close()
        return "Cannot delete: the book is currently borrowed!"

    # Keep borrowing history
    cursor.execute("""
        SELECT loan_id FROM loans
        WHERE book_id = ?
    """, (book_id,))

    if cursor.fetchone():
        conn.close()
        return "Cannot delete: the book has borrowing history!"

    cursor.execute("""
        DELETE FROM books
        WHERE book_id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return "Book deleted successfully!"