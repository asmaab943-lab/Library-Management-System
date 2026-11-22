import os
import sqlite3
import hashlib
import secrets

# مسار الداتا بيز ثابت جنب الملف ده، مهما شغّلتي البرنامج من أي مكان
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

# كلمة مرور مؤقتة لكل حسابات الأدمن
DEFAULT_ADMIN_PASSWORD = "Library@2026"

# كلمة مرور مؤقتة لحسابات اليوزر التجريبية
DEFAULT_USER_PASSWORD = "User@2026"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    )

    return salt + "$" + hashed.hex()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
                CHECK(role IN ('admin', 'user')),
            email TEXT UNIQUE
        )
    """)

    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
                CHECK(available IN (0, 1))
        )
    """)

    # Loans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'borrowed'
                CHECK(status IN ('borrowed', 'returned')),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """)

    # Initial admin accounts
    admins = [
        ("Basmala Salah", "basmalasalah@gmail.com"),
        ("Amira Ellithy", "amiraellithy@gmail.com"),
        ("Asmaa Badran", "asmaabadran@gmail.com"),
        ("Aya Ebrahim", "ayaebrahim@gmail.com"),
        ("Enas Mohamed", "enasmohamed@gmail.com")
    ]

    for username, email in admins:
        cursor.execute("""
            INSERT OR IGNORE INTO users
            (username, password, role, email)
            VALUES (?, ?, 'admin', ?)
        """, (username, hash_password(DEFAULT_ADMIN_PASSWORD), email))

    # Test user accounts (for borrowing / returning)
    test_users = ["aya", "asmaa"]

    for username in test_users:
        cursor.execute("""
            INSERT OR IGNORE INTO users
            (username, password, role)
            VALUES (?, ?, 'user')
        """, (username, hash_password(DEFAULT_USER_PASSWORD)))

    # Default books
    books = [
        ("الفيل الأزرق", "أحمد مراد", "رواية"),
        ("أرض زيكولا", "عمرو عبد الحميد", "رواية"),
        ("تراب الماس", "أحمد مراد", "رواية"),
        ("في قلبي أنثى عبرية", "خولة حمدي", "رواية"),
        ("هيبتا", "محمد صادق", "رواية"),
        ("1984", "George Orwell", "رواية"),
        ("Pride and Prejudice", "Jane Austen", "رواية"),
        ("The Great Gatsby", "F. Scott Fitzgerald", "رواية"),
        ("Frankenstein", "Mary Shelley", "رواية"),
        ("The Little Prince", "Antoine de Saint-Exupery", "رواية")
    ]

    for title, author, category in books:
        cursor.execute("""
            SELECT book_id FROM books
            WHERE title = ? AND author = ?
        """, (title, author))

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO books (title, author, category)
                VALUES (?, ?, ?)
            """, (title, author, category))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database created successfully!")