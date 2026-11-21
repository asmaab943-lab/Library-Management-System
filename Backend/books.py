from data import books


# Add a new book
def add_book(book_id, title, author, category):

    # Check if the book already exists
    for book in books:
        if book["id"] == book_id:
            return "Book already exists!"

    # Create a new book
    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "category": category,
        "available": True
    }

    # Add the book to the list
    books.append(new_book)

    return "Book added successfully!"


# Search for a book
def search_book(title):

    for book in books:
        if title.lower() in book["title"].lower():
            return book

    return "Book not found!"


# Display all books
def display_books():

    if not books:
        return "No books available!"

    for book in books:
        print(book)


# Delete a book
def delete_book(book_id):

    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return "Book deleted successfully!"

    return "Book not found!"