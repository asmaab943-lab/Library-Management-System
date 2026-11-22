import os
import sqlite3
import hashlib
import hmac
import secrets


# تحديد مكان قاعدة البيانات بجانب الملف
DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "library.db"
)

PBKDF2_ITERATIONS = 100000

# كلمة المرور الافتراضية لحسابات الأدمن
DEFAULT_ADMIN_PASSWORD = "Library@2026"


# إنشاء اتصال بقاعدة البيانات
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# تشفير كلمة المرور
def hash_password(password):
    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        PBKDF2_ITERATIONS
    )

    return salt + "$" + hashed.hex()


# التحقق من كلمة المرور
def verify_password(stored_password, provided_password):
    try:
        salt, key_hex = stored_password.split("$", 1)

        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            provided_password.encode(),
            salt.encode(),
            PBKDF2_ITERATIONS
        )

        return hmac.compare_digest(new_key.hex(), key_hex)

    except Exception:
        return False


# إنشاء الجداول وإضافة البيانات الافتراضية
def init_db():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # جدول المستخدمين
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

        # جدول الكتب
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

        # جدول الاستعارات
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

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id),

                FOREIGN KEY (book_id)
                    REFERENCES books(book_id)
            )
        """)

        # منع استعارة الكتاب أكثر من مرة في نفس الوقت
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_loan
                ON loans(book_id)
                WHERE status = 'borrowed'
            """)

        except sqlite3.IntegrityError:
            print(
                "تحذير: توجد كتب عليها أكثر من استعارة نشطة "
                "في البيانات القديمة."
            )

        # حسابات الأدمن الافتراضية
        admins = [
            ("Basmala Salah", "basmalasalah@gmail.com"),
            ("Amira Ellithy", "amiraellithy@gmail.com"),
            ("Asmaa Badran", "asmaabadran@gmail.com"),
            ("Aya Ebrahim", "ayaebrahim@gmail.com"),
            ("Enas Mohamed", "enasmohamed@gmail.com")
        ]

        for username, email in admins:

            cursor.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,)
            )

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT OR IGNORE INTO users
                (username, password, role, email)
                VALUES (?, ?, 'admin', ?)
            """, (
                username,
                hash_password(DEFAULT_ADMIN_PASSWORD),
                email
            ))

        # الكتب الافتراضية
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

    finally:
        conn.close()


# تشغيل الملف مباشرة لإنشاء قاعدة البيانات
if __name__ == "__main__":

    init_db()

    print("Database created successfully!")