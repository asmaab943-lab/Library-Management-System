from datetime import date, timedelta
from schema import get_connection
from auth import check_role


# Borrow a book
def borrow_book(member_name, book_id):

    if not check_role(member_name, "user"):
        return "User not found or not allowed!"

    conn = get_connection()
    cursor = conn.cursor()

    # Get user ID
    cursor.execute("""
        SELECT user_id FROM users
        WHERE username = ?
    """, (member_name,))

    user = cursor.fetchone()

    # Find the book
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
        return "Book is not available!"

    # Set borrowing and due dates
    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=14)

    # Save borrowing information
    cursor.execute("""
        INSERT INTO loans
        (user_id, book_id, borrow_date, due_date, status)
        VALUES (?, ?, ?, ?, 'borrowed')
    """, (
        user[0],
        book_id,
        str(borrow_date),
        str(due_date)
    ))

    # Change book availability
    cursor.execute("""
        UPDATE books
        SET available = 0
        WHERE book_id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return "Book borrowed successfully!"


# Return a book
def return_book(member_name, book_id):

    if not check_role(member_name, "user"):
        return "User not found or not allowed!"

    conn = get_connection()
    cursor = conn.cursor()

    # Get user ID
    cursor.execute("""
        SELECT user_id FROM users
        WHERE username = ?
    """, (member_name,))

    user = cursor.fetchone()

    # Find the borrowing record
    cursor.execute("""
        SELECT loan_id FROM loans
        WHERE user_id = ?
        AND book_id = ?
        AND status = 'borrowed'
    """, (user[0], book_id))

    loan = cursor.fetchone()

    if loan is None:
        conn.close()
        return "No borrowing record found!"

    # Update borrowing record
    cursor.execute("""
        UPDATE loans
        SET status = 'returned',
            return_date = ?
        WHERE loan_id = ?
    """, (str(date.today()), loan[0]))

    # Make the book available again
    cursor.execute("""
        UPDATE books
        SET available = 1
        WHERE book_id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return "Book returned successfully!"