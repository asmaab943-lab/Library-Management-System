from data import books, loans
from auth import check_role
from datetime import date, timedelta


# Borrow a book
def borrow_book(member_name, book_id):

    # Check if the member is a user
    if not check_role(member_name, "user"):
        return "User not found or not allowed!"

    # Find the book
    for book in books:
        if book["id"] == book_id:

            # Check if the book is available
            if book["available"] == False:
                return "Book is not available!"

            # Change book availability
            book["available"] = False

            # Set borrowing and due dates
            borrow_date = date.today()
            due_date = borrow_date + timedelta(days=14)

            # Save borrowing information
            loan = {
                "member": member_name,
                "book_id": book_id,
                "borrow_date": str(borrow_date),
                "due_date": str(due_date)
            }

            loans.append(loan)

            return "Book borrowed successfully!"

    return "Book not found!"


# Return a book
def return_book(member_name, book_id):

    # Check if the member is a user
    if not check_role(member_name, "user"):
        return "User not found or not allowed!"

    # Find the borrowing record
    for loan in loans:
        if loan["member"] == member_name and loan["book_id"] == book_id:

            # Make the book available again
            for book in books:
                if book["id"] == book_id:
                    book["available"] = True

            # Remove the borrowing record
            loans.remove(loan)

            return "Book returned successfully!"

    return "No borrowing record found!"