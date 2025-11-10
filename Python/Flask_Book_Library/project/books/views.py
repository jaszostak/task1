from flask import render_template, Blueprint, request, redirect, url_for, jsonify
from project import db
from project.books.models import Book, _sanitize_text, _validate_year
from project.books.forms import CreateBook

# Blueprint for books
books = Blueprint('books', __name__, template_folder='templates', url_prefix='/books')


# Route to display books in HTML
@books.route('/', methods=['GET'])
def list_books():
    # Fetch all books from the database
    books = Book.query.all()
    print('Books page accessed')
    return render_template('books.html', books=books)


# Route to fetch books in JSON format
@books.route('/json', methods=['GET'])
def list_books_json():
    # Fetch all books from the database and convert to JSON
    books = Book.query.all()
    # Create a list of dictionaries representing each book with the required fields
    book_list = [
        {'name': book.name, 'author': book.author, 'year_published': book.year_published, 'book_type': book.book_type}
        for book in books]
    return jsonify(books=book_list)


# Route to create a new book
@books.route('/create', methods=['POST', 'GET'])
def create_book():
    data = request.get_json(silent=True) or {}

    try:
        name = _sanitize_text(data.get('name'), field="name", maxlen=64)
        author = _sanitize_text(data.get('author'), field="author", maxlen=64)
        year_published = _validate_year(data.get('year_published'))
        book_type = _sanitize_text(data.get('book_type'), field="book_type", maxlen=20)
    except Exception as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400

    new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)

    try:
        # Add the new book to the session and commit to save to the database
        db.session.add(new_book)
        db.session.commit()
        print('Book added successfully')
        return redirect(url_for('books.list_books'))
    except Exception as e:
        # Handle any exceptions, such as database errors
        db.session.rollback()
        print('Error creating book')
        return jsonify({'error': f'Error creating book: {str(e)}'}), 500


# Route to update an existing book
@books.route('/<int:book_id>/edit', methods=['POST'])
def edit_book(book_id):
    # Get the book with the given ID
    book = Book.query.get(book_id)

    # Check if the book exists
    if not book:
        print('Book not found')
        return jsonify({'error': 'Book not found'}), 404

    try:
        # Get data from the request as JSON
        data = request.get_json(silent=True) or {}

        # Update book details
        if 'name' in data:
            book.name = _sanitize_text(data['name'], field="name", maxlen=64)
        if 'author' in data:
            book.author = _sanitize_text(data['author'], field="author", maxlen=64)
        if 'year_published' in data:
            book.year_published = _validate_year(data['year_published'])
        if 'book_type' in data:
            book.book_type = _sanitize_text(data['book_type'], field="book_type", maxlen=20)

        # Commit the changes to the database
        db.session.commit()
        print('Book edited successfully')
        return jsonify({'message': 'Book updated successfully'})
    except Exception as e:
        # Handle any exceptions
        db.session.rollback()
        print('Error updating book')
        return jsonify({'error': f'Error updating book: {str(e)}'}), 400


# Route to fetch existing book data for editing
@books.route('/<int:book_id>/edit-data', methods=['GET'])
def get_book_for_edit(book_id):
    # Get the book with the given ID
    book = Book.query.get(book_id)

    # Check if the book exists
    if not book:
        print('Book not found')
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    # Create a dictionary representing the book data
    book_data = {
        'name': book.name,
        'author': book.author,
        'year_published': book.year_published,
        'book_type': book.book_type
    }

    return jsonify({'success': True, 'book': book_data})


# Route to delete a book
@books.route('/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        print('Book not found')
        return jsonify({'error': 'Book not found'}), 404

    try:
        # Delete the book from the database
        db.session.delete(book)
        db.session.commit()
        print('Book deleted successfully')
        return redirect(url_for('books.list_books'))
    except Exception as e:
        # Handle any exceptions, such as database errors
        db.session.rollback()
        print('Error deleting book')
        return jsonify({'error': f'Error deleting book: {str(e)}'}), 500


# Route to get book details based on book name
@books.route('/details/<string:book_name>', methods=['GET'])
def get_book_details(book_name):
    try:
        safe_name = _sanitize_text(book_name, field="name", maxlen=64)
    except Exception:
        print('Invalid book name')
        return jsonify({'error': 'Invalid book name'}), 400

    # Find the book by its name
    book = Book.query.filter_by(name=safe_name).first()

    if book:
        book_data = {
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'book_type': book.book_type
        }
        return jsonify(book=book_data)
    else:
        print('Book not found')
        return jsonify({'error': 'Book not found'}), 404
