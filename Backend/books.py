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


# Search for books (returns a list of all matches)
def search_book(title):

    results = []

    for book in books:
        if title.lower() in book["title"].lower():
            results.append(book)

    return results


# Display all books (returns the list)
def display_books():

    return list(books)


# Delete a book (not allowed while it is borrowed)
def delete_book(book_id):

    for book in books:
        if book["id"] == book_id:

            if book["available"] == False:
                return "Cannot delete: the book is currently borrowed!"

            books.remove(book)
            return "Book deleted successfully!"

    return "Book not found!"