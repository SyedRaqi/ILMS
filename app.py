import os
import csv
import io
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, flash, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'library.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ilms-dev-secret-key'


@app.after_request
def add_api_headers(response):
    if request.path.startswith('/api/'):
        origin = request.headers.get('Origin')
        if origin in ('http://localhost:5173', 'http://127.0.0.1:5173'):
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def build_book_seed_data():
    titles = [
        'Clean Code', 'Atomic Habits', 'Pride and Prejudice', 'The Alchemist', 'Deep Learning',
        'The Design of Everyday Things', 'The Pragmatic Programmer', 'The Psychology of Money', 'Sapiens',
        'The Secret Life of Bees', 'To Kill a Mockingbird', 'The Fault in Our Stars', 'The Lean Startup',
        'Educated', 'The Hobbit', 'The Little Prince', 'Thinking, Fast and Slow',
        'The 7 Habits of Highly Effective People', 'A Brief History of Time', 'The Kite Runner',
        'The Book Thief', 'Digital Minimalism', 'The Immortal Life of Henrietta Lacks', 'The Silent Patient',
        'The Power of Habit', 'Great Expectations', 'The Road to Wigan Pier', '1984', 'A Tale of Two Cities',
        'The Catcher in the Rye', 'Brave New World', 'The Metamorphosis', 'Animal Farm', 'The Old Man and the Sea',
        'The Secret Garden', 'Jane Eyre', 'Wuthering Heights', 'The Maze Runner', 'The Hunger Games',
        'The Notebook', 'The Book of Five Rings', 'The Art of War', 'Becoming', 'The Martian', 'The Giver',
        'The Glass Castle', 'The Three Musketeers', 'The Count of Monte Cristo', 'Dune', 'Foundation',
        'The Bell Jar', 'The Help', 'Outliers', 'The Black Swan', 'The Sun Also Rises', 'Frankenstein',
        'The Picture of Dorian Gray', 'The Odyssey', 'The Iliad', 'The Secret of the Nagas',
        'The Immortals of Meluha', 'Ikigai', 'The Productivity Project', 'Meditations', 'Man’s Search for Meaning',
        'The Republic', 'A Study in Scarlet', 'The Hound of the Baskervilles', 'And Then There Were None',
        'Murder on the Orient Express', 'The Lost Symbol', 'The Girl with the Dragon Tattoo',
        'The Goldfinch', 'The Secret History', 'Piranesi', 'The Night Circus', 'A Wizard of Earthsea',
        'Mistborn', 'The Name of the Wind', 'The Book of Life', 'The Left Hand of Darkness', 'Neuromancer',
        'Snow Crash', 'The Great Gatsby', 'Death on the Nile', 'The Secret Race', 'Open', 'Born to Run',
        'The Long Run', 'The Big Short', 'The Innovators', 'Algorithms to Live By', 'The Design of Sites',
        'The Visual Display of Quantitative Information', 'The Road', 'The Grapes of Wrath', 'A Clockwork Orange',
        'The Stranger', 'The Trial', 'The Name of the Rose', 'The Handmaid’s Tale', 'Beloved',
        'The Color Purple', 'Their Eyes Were Watching God', 'The Sun Is a Compass', 'A Short History of Nearly Everything',
        'The Universe in a Nutshell', 'The Gene', 'The Animal Farm', 'The Red Badge of Courage',
        'The Consolation of Philosophy', 'A Room of One’s Own', 'The Divine Comedy', 'The Wonderful Wizard of Oz'
    ]

    authors = [
        'Robert C. Martin', 'James Clear', 'Jane Austen', 'Paulo Coelho', 'Ian Goodfellow', 'Don Norman',
        'Andy Hunt', 'Morgan Housel', 'Yuval Noah Harari', 'Sue Monk Kidd', 'Harper Lee', 'John Green',
        'Eric Ries', 'Tara Westover', 'J.R.R. Tolkien', 'Antoine de Saint-Exupéry', 'Daniel Kahneman',
        'Stephen R. Covey', 'Stephen Hawking', 'Khaled Hosseini', 'Markus Zusak', 'Cal Newport',
        'Rebecca Skloot', 'Alex Michaelides', 'Charles Duhigg', 'Charles Dickens', 'George Orwell', 'Aldous Huxley',
        'Franz Kafka', 'Ernest Hemingway', 'Frances Hodgson Burnett', 'Charlotte Brontë', 'Emily Brontë',
        'James Dashner', 'Suzanne Collins', 'Nicholas Sparks', 'Miyamoto Musashi', 'Sun Tzu', 'Michelle Obama',
        'Andy Weir', 'Lois Lowry', 'Jeannette Walls', 'Alexandre Dumas', 'Frank Herbert', 'Isaac Asimov',
        'Sylvia Plath', 'Kathryn Stockett', 'Malcolm Gladwell', 'Nassim Nicholas Taleb', 'Mary Shelley',
        'Oscar Wilde', 'Homer', 'Amish Tripathi', 'Héctor García', 'Chris Bailey', 'Marcus Aurelius',
        'Viktor E. Frankl', 'Plato', 'Arthur Conan Doyle', 'Agatha Christie', 'Dan Brown', 'Stieg Larsson',
        'Donna Tartt', 'Susanna Clarke', 'Erin Morgenstern', 'Ursula K. Le Guin', 'William Gibson',
        'Neal Stephenson', 'F. Scott Fitzgerald', 'Tyler Hamilton', 'Andre Agassi', 'Christopher McDougall',
        'Matt Long', 'Michael Lewis', 'Walter Isaacson', 'Brian Christian', 'Douglas Van Duyne',
        'Edward Tufte', 'Cormac McCarthy', 'John Steinbeck', 'Anthony Burgess', 'Albert Camus', 'Umberto Eco',
        'Margaret Atwood', 'Toni Morrison', 'Alice Walker', 'Zora Neale Hurston', 'Caroline Van Hemert',
        'Bill Bryson', 'Siddhartha Mukherjee', 'Stephen King', 'Virginia Woolf', 'Dante Alighieri', 'L. Frank Baum'
    ]

    categories = [
        'Technology', 'Self Growth', 'Literature', 'Fiction', 'Science', 'Technology', 'Technology', 'Business',
        'History', 'Fiction', 'Literature', 'Fiction', 'Business', 'Biography', 'Fantasy', 'Philosophy',
        'Psychology', 'Self Growth', 'Science', 'Fiction', 'Historical Fiction', 'Technology', 'Science',
        'Thriller', 'Self Growth', 'Literature', 'History', 'Dystopian', 'Classics', 'Literature', 'Classic',
        'Fantasy', 'Literature', 'Classic', 'Children', 'Classic', 'Classic', 'Science Fiction', 'Young Adult',
        'Romance', 'Philosophy', 'Strategy', 'Biography', 'Science Fiction', 'Young Adult', 'Memoir',
        'Adventure', 'Adventure', 'Science Fiction', 'Science Fiction', 'Classic', 'Historical Fiction', 'Psychology',
        'Business', 'Classic', 'Mythology', 'Mythology', 'Self Growth', 'Self Growth', 'Self Growth', 'Philosophy',
        'Philosophy', 'Philosophy', 'Mystery', 'Mystery', 'Mystery', 'Mystery', 'Thriller', 'Thriller',
        'Fiction', 'Fiction', 'Fiction', 'Fantasy', 'Fantasy', 'Fantasy', 'Fantasy', 'Science Fiction',
        'Science Fiction', 'Science Fiction', 'Classic', 'Mystery', 'Sports', 'Sports', 'Sports', 'Fitness',
        'Business', 'Technology', 'Technology', 'Design', 'Design', 'Fiction', 'Classic', 'Classic', 'Philosophy',
        'Classic', 'Historical Fiction', 'Dystopian', 'Literature', 'Literature', 'Literature', 'Nature',
        'Science', 'Science', 'Science', 'Political Fiction', 'History', 'Philosophy', 'Literature', 'Poetry', 'Fantasy'
    ]

    covers = [
        'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1526243741027-444d633d7365?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80'
    ] * 4

    books = []
    for index in range(100):
        title = titles[index]
        author = authors[index % len(authors)]
        category = categories[index]
        isbn = f'978-{1000000000 + index}'
        rating = round(3.5 + ((index % 11) / 10), 1)
        copies = 2 + (index % 6)
        cover = covers[index % len(covers)]
        description = f'{title} explores ideas around {category.lower()} through a compelling and immersive reading experience.'
        books.append((title, author, category, isbn, 'Available', rating, copies, cover, description))
    return books


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                student_id TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        user_columns = [row['name'] for row in conn.execute('PRAGMA table_info(users)').fetchall()]
        if 'role' not in user_columns:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'member'")
            except sqlite3.OperationalError as error:
                if 'duplicate column name' not in str(error).lower():
                    raise
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'Available',
                rating REAL DEFAULT 0,
                copies INTEGER NOT NULL DEFAULT 1,
                cover TEXT,
                description TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS borrow_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                returned_at TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'Issued',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified_at TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            """
        )

        book_count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
        if book_count < 100:
            conn.execute('DELETE FROM books')
            conn.executemany(
                """
                INSERT INTO books (title, author, category, isbn, status, rating, copies, cover, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                build_book_seed_data(),
            )
            conn.commit()

        admin = conn.execute('SELECT id FROM users WHERE email = ?', ('admin@ilms.edu',)).fetchone()
        if not admin:
            conn.execute(
                'INSERT INTO users (full_name, student_id, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
                ('Library Administrator', 'ADMIN001', 'admin@ilms.edu', '', generate_password_hash('admin123'), 'admin'),
            )
            conn.commit()

        librarian = conn.execute('SELECT id FROM users WHERE email = ?', ('librarian@ilms.edu',)).fetchone()
        if not librarian:
            conn.execute(
                'INSERT INTO users (full_name, student_id, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
                ('Library Librarian', 'LIB001', 'librarian@ilms.edu', '', generate_password_hash('librarian123'), 'librarian'),
            )
            conn.commit()


with app.app_context():
    init_db()


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    with get_db() as conn:
        return conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


def login_required(view):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


def admin_required(view):
    @login_required
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user['role'] != 'admin':
            flash('Administrator access is required.', 'error')
            return redirect(url_for('dashboard'))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


def staff_required(view):
    @login_required
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user['role'] not in ('admin', 'librarian'):
            flash('Staff access is required.', 'error')
            return redirect(url_for('dashboard'))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


def calculate_fine(due_date, returned_at=None):
    if not due_date:
        return 0
    end_time = datetime.strptime(returned_at, '%Y-%m-%d %H:%M:%S') if returned_at else datetime.now()
    overdue_days = max(0, (end_time - datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')).days)
    return overdue_days * 5


def notify_available_reservations(conn, book_id, available_copies):
    notified_count = conn.execute(
        "SELECT COUNT(*) FROM reservations WHERE book_id = ? AND status = 'Notified'",
        (book_id,),
    ).fetchone()[0]
    notification_slots = max(0, available_copies - notified_count)
    waiting_reservations = conn.execute(
        "SELECT id FROM reservations WHERE book_id = ? AND status = 'Pending' ORDER BY created_at, id LIMIT ?",
        (book_id, notification_slots),
    ).fetchall()
    for reservation in waiting_reservations:
        conn.execute(
            "UPDATE reservations SET status = 'Notified', notified_at = CURRENT_TIMESTAMP WHERE id = ?",
            (reservation['id'],),
        )
    return len(waiting_reservations)


@app.route('/')
def home():
    with get_db() as conn:
        books = conn.execute('SELECT * FROM books ORDER BY id LIMIT 4').fetchall()
    return render_template('index.html', books=[dict(book) for book in books])


@app.route('/api/books')
def api_books():
    try:
        limit = min(100, max(1, int(request.args.get('limit', 100))))
    except ValueError:
        limit = 100
    query = request.args.get('q', '').strip()
    with get_db() as conn:
        if query:
            books = conn.execute(
                '''
                SELECT * FROM books
                WHERE title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ?
                ORDER BY title LIMIT ?
                ''',
                tuple([f'%{query}%'] * 4) + (limit,),
            ).fetchall()
        else:
            books = conn.execute('SELECT * FROM books ORDER BY title LIMIT ?', (limit,)).fetchall()
    return {'books': [dict(book) for book in books], 'count': len(books)}


@app.route('/api/admin/overview')
@staff_required
def api_admin_overview():
    with get_db() as conn:
        members = conn.execute(
            "SELECT id, full_name, student_id, email, phone, created_at FROM users WHERE role = 'member' ORDER BY created_at DESC"
        ).fetchall()
        books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
        issues = conn.execute(
            '''
            SELECT br.id, br.issued_at, br.due_date, br.returned_at, br.status,
                   u.full_name, u.student_id, b.title, b.author
            FROM borrow_records br JOIN users u ON u.id = br.user_id JOIN books b ON b.id = br.book_id
            ORDER BY br.issued_at DESC
            '''
        ).fetchall()
        reservations = conn.execute(
            '''
            SELECT r.id, r.status, r.created_at, u.full_name, u.student_id, b.title
            FROM reservations r JOIN users u ON u.id = r.user_id JOIN books b ON b.id = r.book_id
            ORDER BY r.created_at DESC
            '''
        ).fetchall()
    issue_data = [dict(issue) for issue in issues]
    for issue in issue_data:
        issue['fine'] = calculate_fine(issue['due_date'], issue['returned_at'])
    return {
        'members': [dict(member) for member in members],
        'books': [dict(book) for book in books],
        'issues': issue_data,
        'reservations': [dict(item) for item in reservations],
        'stats': {
            'members': len(members),
            'books': len(books),
            'issued': sum(1 for issue in issue_data if not issue['returned_at']),
            'fines': sum(issue['fine'] for issue in issue_data),
        },
    }


@app.route('/api/admin/books', methods=['POST'])
@staff_required
def api_add_book():
    payload = request.get_json(silent=True) or {}
    title = str(payload.get('title', '')).strip()
    author = str(payload.get('author', '')).strip()
    category = str(payload.get('category', '')).strip()
    isbn = str(payload.get('isbn', '')).strip()
    cover = str(payload.get('cover', '')).strip()
    description = str(payload.get('description', '')).strip()
    try:
        copies = max(1, int(payload.get('copies', 1)))
    except (TypeError, ValueError):
        copies = 1
    if not all([title, author, category, isbn]):
        return {'error': 'Title, author, category, and ISBN are required.'}, 400
    with get_db() as conn:
        try:
            cursor = conn.execute(
                '''INSERT INTO books (title, author, category, isbn, status, rating, copies, cover, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (title, author, category, isbn, 'Available', 0, copies, cover or None, description or 'Added by library staff.'),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return {'error': 'A book with this ISBN already exists.'}, 409
    return {'message': 'Book added successfully.', 'book_id': cursor.lastrowid}, 201


@app.route('/api/admin/issue', methods=['POST'])
@staff_required
def api_staff_issue():
    payload = request.get_json(silent=True) or {}
    try:
        member_id = int(payload.get('member_id'))
        book_id = int(payload.get('book_id'))
    except (TypeError, ValueError):
        return {'error': 'A member and book are required.'}, 400

    with get_db() as conn:
        member = conn.execute("SELECT id FROM users WHERE id = ? AND role = 'member'", (member_id,)).fetchone()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not member or not book:
            return {'error': 'Member or book not found.'}, 404
        active = conn.execute(
            'SELECT id FROM borrow_records WHERE user_id = ? AND book_id = ? AND returned_at IS NULL',
            (member_id, book_id),
        ).fetchone()
        if active:
            return {'error': 'This member already has this book.'}, 409
        if int(book['copies']) <= 0:
            return {'error': 'No copies are available. Create a reservation instead.'}, 409
        notified_reservation = conn.execute(
            "SELECT id FROM reservations WHERE user_id = ? AND book_id = ? AND status = 'Notified'",
            (member_id, book_id),
        ).fetchone()
        notified_count = conn.execute(
            "SELECT COUNT(*) FROM reservations WHERE book_id = ? AND status = 'Notified'",
            (book_id,),
        ).fetchone()[0]
        if notified_count >= int(book['copies']) and not notified_reservation:
            return {'error': 'Available copies are being held for members with reservations.'}, 409
        due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO borrow_records (user_id, book_id, due_date, status) VALUES (?, ?, ?, ?)',
            (member_id, book_id, due_date, 'Issued'),
        )
        if notified_reservation:
            conn.execute("UPDATE reservations SET status = 'Fulfilled' WHERE id = ?", (notified_reservation['id'],))
        remaining_copies = int(book['copies']) - 1
        conn.execute(
            'UPDATE books SET copies = ?, status = ? WHERE id = ?',
            (remaining_copies, 'Available' if remaining_copies else 'Issued', book_id),
        )
        notify_available_reservations(conn, book_id, remaining_copies)
        conn.commit()
    return {'message': 'Book issued successfully.', 'due_date': due_date}, 201


@app.route('/api/admin/reserve', methods=['POST'])
@staff_required
def api_staff_reserve():
    payload = request.get_json(silent=True) or {}
    try:
        member_id = int(payload.get('member_id'))
        book_id = int(payload.get('book_id'))
    except (TypeError, ValueError):
        return {'error': 'A member and book are required.'}, 400

    with get_db() as conn:
        member = conn.execute("SELECT id FROM users WHERE id = ? AND role = 'member'", (member_id,)).fetchone()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not member or not book:
            return {'error': 'Member or book not found.'}, 404
        if int(book['copies']) > 0:
            return {'error': 'This book is available to issue now.'}, 409
        existing = conn.execute(
            "SELECT id FROM reservations WHERE user_id = ? AND book_id = ? AND status IN ('Pending', 'Notified')",
            (member_id, book_id),
        ).fetchone()
        if existing:
            return {'error': 'This member already has an active reservation.'}, 409
        conn.execute(
            'INSERT INTO reservations (user_id, book_id, status) VALUES (?, ?, ?)',
            (member_id, book_id, 'Pending'),
        )
        conn.commit()
    return {'message': 'Reservation created successfully.'}, 201


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next') or ''
    if not (next_url.startswith('/') and not next_url.startswith('//')):
        next_url = ''
    if request.method == 'GET' and session.get('user_id') and next_url:
        return redirect(next_url)
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            flash('Login successful.', 'success')
            if next_url:
                return redirect(next_url)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user['role'] == 'librarian':
                return redirect(url_for('librarian_dashboard'))
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'error')
        return render_template('login.html', next_url=next_url)

    return render_template('login.html', next_url=next_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([full_name, student_id, email, password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        with get_db() as conn:
            existing = conn.execute(
                'SELECT id FROM users WHERE email = ? OR student_id = ?',
                (email, student_id),
            ).fetchone()
            if existing:
                flash('A user with this email or student ID already exists.', 'error')
                return render_template('register.html')

            password_hash = generate_password_hash(password)
            cursor = conn.execute(
                'INSERT INTO users (full_name, student_id, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
                (full_name, student_id, email, phone, password_hash, 'member'),
            )
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['user_name'] = full_name
            conn.commit()

        flash('Registration successful.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    with get_db() as conn:
        borrow_count = conn.execute(
            "SELECT COUNT(*) FROM borrow_records WHERE user_id = ? AND returned_at IS NULL",
            (user['id'],),
        ).fetchone()[0]
        all_books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
        my_books = conn.execute(
            '''
            SELECT b.title, b.author, br.status, br.due_date, br.id
            FROM borrow_records br
            JOIN books b ON b.id = br.book_id
            WHERE br.user_id = ? AND br.returned_at IS NULL
            ORDER BY br.issued_at DESC
            ''',
            (user['id'],),
        ).fetchall()
        my_reservations = conn.execute(
            '''
            SELECT r.id, r.status, r.created_at, b.title, b.author
            FROM reservations r
            JOIN books b ON b.id = r.book_id
            WHERE r.user_id = ? AND r.status IN ('Pending', 'Notified')
            ORDER BY r.created_at DESC
            ''',
            (user['id'],),
        ).fetchall()

    pending_fines = sum(calculate_fine(book['due_date']) for book in my_books)
    due_soon = sum(
        1 for book in my_books
        if book['due_date'] and datetime.strptime(book['due_date'], '%Y-%m-%d %H:%M:%S') <= datetime.now() + timedelta(days=3)
    )

    stats = [
        {'label': 'Books Borrowed', 'value': str(borrow_count), 'trend': '+12%'},
        {'label': 'Active Reservations', 'value': str(len(my_reservations)), 'trend': 'Queue status'},
        {'label': 'Pending Fines', 'value': f'INR {pending_fines}', 'trend': 'INR 5 per day'},
        {'label': 'Books Due Soon', 'value': str(due_soon), 'trend': 'Next 3 days'},
    ]
    return render_template(
        'dashboard.html',
        stats=stats,
        books=[dict(book) for book in all_books],
        my_books=[dict(item) for item in my_books],
        reservations=[dict(item) for item in my_reservations],
        user=user,
    )


@app.route('/books')
def books():
    with get_db() as conn:
        books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    return render_template('books.html', books=[dict(book) for book in books], user=current_user())


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    with get_db() as conn:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            return redirect(url_for('books'))
        related = conn.execute(
            'SELECT * FROM books WHERE id != ? ORDER BY rating DESC LIMIT 3',
            (book_id,),
        ).fetchall()
    return render_template('book_detail.html', book=dict(book), related=[dict(item) for item in related], user=current_user())


@app.route('/issue/<int:book_id>', methods=['POST'])
@login_required
def issue_book(book_id):
    user = current_user()
    if user['role'] != 'member':
        flash('Staff accounts must issue books from the staff desk.', 'error')
        return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'librarian_dashboard'))
    with get_db() as conn:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            flash('Book not found.', 'error')
            return redirect(url_for('books'))

        active_record = conn.execute(
            'SELECT * FROM borrow_records WHERE user_id = ? AND book_id = ? AND returned_at IS NULL',
            (user['id'], book_id),
        ).fetchone()
        if active_record:
            flash('This book is already issued to you.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))

        if book['copies'] <= 0:
            flash('No copies of this book are currently available.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))

        notified_reservation = conn.execute(
            "SELECT id FROM reservations WHERE user_id = ? AND book_id = ? AND status = 'Notified'",
            (user['id'], book_id),
        ).fetchone()
        notified_count = conn.execute(
            "SELECT COUNT(*) FROM reservations WHERE book_id = ? AND status = 'Notified'",
            (book_id,),
        ).fetchone()[0]
        if notified_count >= int(book['copies']) and not notified_reservation:
            flash('An available copy is being held for a member who reserved it.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))

        due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO borrow_records (user_id, book_id, due_date, status) VALUES (?, ?, ?, ?)',
            (user['id'], book_id, due_date, 'Issued'),
        )
        if notified_reservation:
            conn.execute("UPDATE reservations SET status = 'Fulfilled' WHERE id = ?", (notified_reservation['id'],))
        remaining_copies = max(0, int(book['copies']) - 1)
        new_status = 'Available' if remaining_copies > 0 else 'Issued'
        conn.execute(
            'UPDATE books SET copies = ?, status = ? WHERE id = ?',
            (remaining_copies, new_status, book_id),
        )
        notify_available_reservations(conn, book_id, remaining_copies)
        conn.commit()

    flash('Book issued successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/return/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    user = current_user()
    with get_db() as conn:
        record = conn.execute(
            'SELECT * FROM borrow_records WHERE user_id = ? AND book_id = ? AND returned_at IS NULL ORDER BY issued_at DESC LIMIT 1',
            (user['id'], book_id),
        ).fetchone()
        if not record:
            flash('No active issue found for this book.', 'error')
            return redirect(url_for('dashboard'))

        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        updated_copies = int(book['copies']) + 1
        conn.execute(
            'UPDATE borrow_records SET returned_at = CURRENT_TIMESTAMP, status = ? WHERE id = ?',
            ('Returned', record['id']),
        )
        conn.execute(
            'UPDATE books SET copies = ?, status = ? WHERE id = ?',
            (updated_copies, 'Available', book_id),
        )
        notified_count = notify_available_reservations(conn, book_id, updated_copies)
        conn.commit()

    if notified_count:
        flash('Book returned successfully. Reservation notification sent.', 'success')
    else:
        flash('Book returned successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book(book_id):
    user = current_user()
    if user['role'] != 'member':
        flash('Staff accounts must manage reservations from the staff desk.', 'error')
        return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'librarian_dashboard'))
    with get_db() as conn:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            flash('Book not found.', 'error')
            return redirect(url_for('books'))
        if int(book['copies']) > 0:
            flash('This book is available to issue now.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        existing = conn.execute(
            "SELECT id FROM reservations WHERE user_id = ? AND book_id = ? AND status IN ('Pending', 'Notified')",
            (user['id'], book_id),
        ).fetchone()
        if existing:
            flash('You already have an active reservation for this book.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        conn.execute(
            'INSERT INTO reservations (user_id, book_id, status) VALUES (?, ?, ?)',
            (user['id'], book_id, 'Pending'),
        )
        conn.commit()

    flash('Reservation created.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    with get_db() as conn:
        members = conn.execute(
            "SELECT id, full_name, student_id, email, phone, created_at FROM users WHERE role = 'member' ORDER BY created_at DESC"
        ).fetchall()
        issued_records = conn.execute(
            '''
            SELECT br.id, br.issued_at, br.due_date, br.returned_at, br.status,
                   u.full_name, u.student_id, u.email, b.title, b.author
            FROM borrow_records br
            JOIN users u ON u.id = br.user_id
            JOIN books b ON b.id = br.book_id
            ORDER BY br.issued_at DESC
            '''
        ).fetchall()
        books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
        reservations = conn.execute(
            '''
            SELECT r.id, r.status, r.created_at, u.full_name, u.student_id, b.title
            FROM reservations r
            JOIN users u ON u.id = r.user_id
            JOIN books b ON b.id = r.book_id
            ORDER BY r.created_at DESC
            '''
        ).fetchall()

    issues = []
    total_fines = 0
    for record in issued_records:
        item = dict(record)
        item['fine'] = calculate_fine(item['due_date'], item['returned_at'])
        total_fines += item['fine']
        issues.append(item)
    active_issues = [issue for issue in issues if not issue['returned_at']]

    return render_template(
        'admin.html',
        members=[dict(member) for member in members],
        issues=issues,
        active_issues=active_issues,
        books=[dict(book) for book in books],
        reservations=[dict(item) for item in reservations],
        total_fines=total_fines,
        admin=current_user(),
    )


@app.route('/admin/options')
@admin_required
def admin_options():
    with get_db() as conn:
        issued_records = conn.execute(
            '''
            SELECT br.id, br.issued_at, br.due_date, u.full_name, u.student_id, b.title, b.author
            FROM borrow_records br
            JOIN users u ON u.id = br.user_id
            JOIN books b ON b.id = br.book_id
            WHERE br.returned_at IS NULL
            ORDER BY br.issued_at DESC
            '''
        ).fetchall()
        reservations = conn.execute(
            '''
            SELECT r.id, r.status, r.created_at, u.full_name, u.student_id, b.title, b.author
            FROM reservations r
            JOIN users u ON u.id = r.user_id
            JOIN books b ON b.id = r.book_id
            WHERE r.status IN ('Pending', 'Notified')
            ORDER BY r.created_at DESC
            '''
        ).fetchall()
    return render_template(
        'admin_options.html',
        admin=current_user(),
        issues=[dict(record) for record in issued_records],
        reservations=[dict(item) for item in reservations],
    )


@app.route('/admin/issues/<int:issue_id>/remove', methods=['POST'])
@admin_required
def remove_issued_book(issue_id):
    with get_db() as conn:
        record = conn.execute(
            'SELECT book_id FROM borrow_records WHERE id = ? AND returned_at IS NULL',
            (issue_id,),
        ).fetchone()
        if not record:
            flash('Active issue not found.', 'error')
            endpoint = 'admin_dashboard' if request.form.get('return_to') == 'admin' else 'admin_options'
            return redirect(url_for(endpoint))

        book = conn.execute('SELECT copies FROM books WHERE id = ?', (record['book_id'],)).fetchone()
        copies = int(book['copies']) + 1
        conn.execute(
            'UPDATE borrow_records SET returned_at = CURRENT_TIMESTAMP, status = ? WHERE id = ?',
            ('Returned', issue_id),
        )
        conn.execute(
            'UPDATE books SET copies = ?, status = ? WHERE id = ?',
            (copies, 'Available', record['book_id']),
        )
        notified_count = notify_available_reservations(conn, record['book_id'], copies)
        conn.commit()
    if notified_count:
        flash(f'Book returned. {notified_count} reservation notification(s) sent.', 'success')
    else:
        flash('Book returned and removed from active issues.', 'success')
    endpoint = 'admin_dashboard' if request.form.get('return_to') == 'admin' else 'admin_options'
    return redirect(url_for(endpoint))


@app.route('/admin/reservations/<int:reservation_id>/remove', methods=['POST'])
@admin_required
def remove_reservation(reservation_id):
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE reservations SET status = 'Cancelled' WHERE id = ? AND status IN ('Pending', 'Notified')",
            (reservation_id,),
        )
        if cursor.rowcount == 0:
            flash('Active reservation not found.', 'error')
            return redirect(url_for('admin_options'))
        conn.commit()
    flash('Reservation removed from the active queue.', 'success')
    return redirect(url_for('admin_options'))


@app.route('/librarian')
@staff_required
def librarian_dashboard():
    with get_db() as conn:
        members = conn.execute(
            "SELECT id, full_name, student_id, email, phone, created_at FROM users WHERE role = 'member' ORDER BY created_at DESC"
        ).fetchall()
        issued_records = conn.execute(
            '''
            SELECT br.id, br.issued_at, br.due_date, br.returned_at, br.status,
                   u.full_name, u.student_id, u.email, b.title, b.author
            FROM borrow_records br
            JOIN users u ON u.id = br.user_id
            JOIN books b ON b.id = br.book_id
            ORDER BY br.issued_at DESC
            '''
        ).fetchall()
        books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
        reservations = conn.execute(
            '''
            SELECT r.id, r.status, r.created_at, u.full_name, u.student_id, b.title
            FROM reservations r
            JOIN users u ON u.id = r.user_id
            JOIN books b ON b.id = r.book_id
            ORDER BY r.created_at DESC
            '''
        ).fetchall()

    issues = []
    total_fines = 0
    for record in issued_records:
        item = dict(record)
        item['fine'] = calculate_fine(item['due_date'], item['returned_at'])
        total_fines += item['fine']
        issues.append(item)
    active_issues = [issue for issue in issues if not issue['returned_at']]

    return render_template(
        'admin.html',
        members=[dict(member) for member in members],
        issues=issues,
        active_issues=active_issues,
        books=[dict(book) for book in books],
        reservations=[dict(item) for item in reservations],
        total_fines=total_fines,
        admin=current_user(),
    )


@app.route('/admin/books/add', methods=['POST'])
@admin_required
def add_book():
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    category = request.form.get('category', '').strip()
    isbn = request.form.get('isbn', '').strip()
    cover = request.form.get('cover', '').strip()
    description = request.form.get('description', '').strip()
    try:
        copies = max(1, int(request.form.get('copies', '1')))
    except ValueError:
        copies = 1

    if not all([title, author, category, isbn]):
        flash('Title, author, category, and ISBN are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    with get_db() as conn:
        try:
            conn.execute(
                '''
                INSERT INTO books (title, author, category, isbn, status, rating, copies, cover, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (title, author, category, isbn, 'Available', 0, copies, cover or None, description or 'Added by the library administrator.'),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash('A book with this ISBN already exists.', 'error')
            return redirect(url_for('admin_dashboard'))

    flash('Book added to the collection.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/reports')
@admin_required
def reports():
    with get_db() as conn:
        total_books = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
        available_books = conn.execute("SELECT COUNT(*) FROM books WHERE status = 'Available'").fetchone()[0]
        issued_books = conn.execute("SELECT COUNT(*) FROM borrow_records WHERE returned_at IS NULL").fetchone()[0]
        active_members = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'member'").fetchone()[0]
        category_rows = conn.execute(
            'SELECT category, COUNT(*) AS total FROM books GROUP BY category ORDER BY total DESC LIMIT 8'
        ).fetchall()
        returned_books = conn.execute("SELECT COUNT(*) FROM borrow_records WHERE returned_at IS NOT NULL").fetchone()[0]
        overdue_rows = conn.execute(
            "SELECT COUNT(*) FROM borrow_records WHERE returned_at IS NULL AND due_date < datetime('now')"
        ).fetchone()[0]
        reservation_count = conn.execute(
            "SELECT COUNT(*) FROM reservations WHERE status IN ('Pending', 'Notified')"
        ).fetchone()[0]

    report_data = {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'active_members': active_members,
        'returned_books': returned_books,
        'overdue_books': overdue_rows,
        'reservations': reservation_count,
        'categories': [dict(row) for row in category_rows],
    }
    return render_template('reports.html', report_data=report_data)


@app.route('/reports/export/<report_type>')
@admin_required
def export_report(report_type):
    queries = {
        'books': (
            'books.csv',
            ['Title', 'Author', 'Category', 'ISBN', 'Status', 'Copies'],
            'SELECT title, author, category, isbn, status, copies FROM books ORDER BY title',
        ),
        'members': (
            'members.csv',
            ['Name', 'Student ID', 'Email', 'Phone', 'Role', 'Joined'],
            "SELECT full_name, student_id, email, phone, role, created_at FROM users WHERE role = 'member' ORDER BY full_name",
        ),
        'circulation': (
            'circulation.csv',
            ['Member', 'Book', 'Issued', 'Due', 'Returned', 'Status'],
            '''
            SELECT u.full_name, b.title, br.issued_at, br.due_date,
                   br.returned_at, br.status
            FROM borrow_records br
            JOIN users u ON u.id = br.user_id
            JOIN books b ON b.id = br.book_id
            ORDER BY br.issued_at DESC
            ''',
        ),
    }
    if report_type not in queries:
        return redirect(url_for('reports'))

    filename, headers, query = queries[report_type]
    with get_db() as conn:
        rows = conn.execute(query).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows([tuple(row) for row in rows])
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
