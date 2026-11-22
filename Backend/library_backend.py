import sqlite3

from contextlib import contextmanager
from datetime import date, timedelta

from Database.schema import (
    get_connection,
    hash_password,
    verify_password
)


# كل الدوال التي تغير البيانات ترجع:
# (success, message)

MIN_PASSWORD_LENGTH = 6


# إدارة الاتصال بقاعدة البيانات
@contextmanager
def db():

    conn = get_connection()

    try:
        yield conn

    finally:
        conn.close()


# ---------------- المستخدمين والصلاحيات ----------------

# الحصول على صلاحية المستخدم
def get_role(username):

    with db() as conn:

        row = conn.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    return row[0] if row else None


# التحقق من صلاحية المستخدم
def check_role(username, required_role):

    return get_role(username) == required_role


# تسجيل الدخول والتحقق من البيانات
def authenticate(username, password):

    with db() as conn:

        row = conn.execute(
            "SELECT password, role FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if row and verify_password(row[0], password):

        return row[1]

    return None


# تسجيل عضو جديد
def register_member(username, password):

    username = username.strip()

    if not username or not password:

        return False, "أدخل البيانات كاملة."

    if len(password) < MIN_PASSWORD_LENGTH:

        return False, (
            f"كلمة المرور لازم تكون "
            f"{MIN_PASSWORD_LENGTH} حروف على الأقل."
        )

    try:

        with db() as conn:

            conn.execute(
                """
                INSERT INTO users (username, password, role)
                VALUES (?, ?, 'user')
                """,
                (username, hash_password(password))
            )

            conn.commit()

    except sqlite3.IntegrityError:

        return False, "اسم المستخدم موجود بالفعل."

    return True, "تم إنشاء حساب العضو بنجاح!"


# الحصول على أسماء الأعضاء
def get_member_names():

    with db() as conn:

        rows = conn.execute(
            """
            SELECT username
            FROM users
            WHERE role = 'user'
            ORDER BY username
            """
        ).fetchall()

    return [r[0] for r in rows]


# ---------------- الكتب ----------------

# الحصول على رقم الكتاب التالي
def get_next_book_id():

    with db() as conn:

        return conn.execute(
            "SELECT COALESCE(MAX(book_id), 0) + 1 FROM books"
        ).fetchone()[0]


# تحويل بيانات الكتب إلى Dictionary
def _rows_to_books(rows):

    return [
        {
            "id": r[0],
            "title": r[1],
            "author": r[2],
            "category": r[3],
            "available": bool(r[4]),
        }
        for r in rows
    ]


# عرض جميع الكتب
def display_books():

    with db() as conn:

        rows = conn.execute(
            """
            SELECT book_id, title, author, category, available
            FROM books
            """
        ).fetchall()

    return _rows_to_books(rows)


# البحث عن كتاب
def search_book(query):

    pattern = "%" + query + "%"

    with db() as conn:

        rows = conn.execute(
            """
            SELECT book_id, title, author, category, available
            FROM books
            WHERE title LIKE ?
            OR author LIKE ?
            OR category LIKE ?
            """,
            (pattern, pattern, pattern)
        ).fetchall()

    return _rows_to_books(rows)


# إضافة كتاب جديد
def add_book(actor, book_id, title, author, category):

    if not check_role(actor, "admin"):

        return False, "غير مسموح: الأدمن فقط يقدر يضيف كتب."

    try:

        with db() as conn:

            exists = conn.execute(
                "SELECT 1 FROM books WHERE book_id = ?",
                (book_id,)
            ).fetchone()

            if exists:

                return False, "Book already exists!"

            conn.execute(
                """
                INSERT INTO books
                (book_id, title, author, category)
                VALUES (?, ?, ?, ?)
                """,
                (book_id, title, author, category)
            )

            conn.commit()

    except sqlite3.IntegrityError as e:

        return False, f"تعذر إضافة الكتاب: {e}"

    return True, "Book added successfully!"


# حذف كتاب
def delete_book(actor, book_id):

    if not check_role(actor, "admin"):

        return False, "غير مسموح: الأدمن فقط يقدر يحذف كتب."

    with db() as conn:

        book = conn.execute(
            "SELECT available FROM books WHERE book_id = ?",
            (book_id,)
        ).fetchone()

        if book is None:

            return False, "Book not found!"

        if book[0] == 0:

            return False, (
                "Cannot delete: the book is currently borrowed!"
            )

        # التأكد من عدم وجود سجل استعارات سابق
        has_history = conn.execute(
            "SELECT 1 FROM loans WHERE book_id = ?",
            (book_id,)
        ).fetchone()

        if has_history:

            return False, (
                "Cannot delete: the book has borrowing history!"
            )

        conn.execute(
            "DELETE FROM books WHERE book_id = ?",
            (book_id,)
        )

        conn.commit()

    return True, "Book deleted successfully!"


# ---------------- الاستعارة والإرجاع ----------------

# التحقق من صلاحية العضو للاستعارة أو الإرجاع
def _check_member_permission(actor, member_name):

    actor_role = get_role(actor)

    if actor_role is None:

        return "المستخدم غير موجود."

    if actor_role == "user" and actor != member_name:

        return (
            "غير مسموح: تقدر تستعير وترجّع بحسابك أنت فقط."
        )

    if get_role(member_name) != "user":

        return "User not found or not allowed!"

    return None


# استعارة كتاب
def borrow_book(actor, member_name, book_id):

    error = _check_member_permission(actor, member_name)

    if error:

        return False, error

    with db() as conn:

        user = conn.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (member_name,)
        ).fetchone()

        book = conn.execute(
            "SELECT 1 FROM books WHERE book_id = ?",
            (book_id,)
        ).fetchone()

        if book is None:

            return False, "Book not found!"

        borrow_date = date.today()

        due_date = borrow_date + timedelta(days=14)

        try:

            # تحديث حالة الكتاب إذا كان متاحاً فقط
            cur = conn.execute(
                """
                UPDATE books
                SET available = 0
                WHERE book_id = ? AND available = 1
                """,
                (book_id,)
            )

            if cur.rowcount == 0:

                conn.rollback()

                return False, "Book is not available!"

            conn.execute(
                """
                INSERT INTO loans
                (user_id, book_id, borrow_date, due_date, status)
                VALUES (?, ?, ?, ?, 'borrowed')
                """,
                (
                    user[0],
                    book_id,
                    str(borrow_date),
                    str(due_date)
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.rollback()

            return False, "Book is not available!"

    return True, "Book borrowed successfully!"


# إرجاع كتاب
def return_book(actor, member_name, book_id):

    error = _check_member_permission(actor, member_name)

    if error:

        return False, error

    with db() as conn:

        user = conn.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (member_name,)
        ).fetchone()

        loan = conn.execute(
            """
            SELECT loan_id
            FROM loans
            WHERE user_id = ?
            AND book_id = ?
            AND status = 'borrowed'
            """,
            (user[0], book_id)
        ).fetchone()

        if loan is None:

            return False, "No borrowing record found!"

        conn.execute(
            """
            UPDATE loans
            SET status = 'returned', return_date = ?
            WHERE loan_id = ?
            """,
            (str(date.today()), loan[0])
        )

        conn.execute(
            "UPDATE books SET available = 1 WHERE book_id = ?",
            (book_id,)
        )

        conn.commit()

    return True, "Book returned successfully!"


# عرض الاستعارات الحالية
def get_current_loans(actor):

    role = get_role(actor)

    if role is None:

        return []

    query = """
        SELECT
            u.username,
            b.title,
            l.borrow_date,
            l.due_date,
            b.book_id

        FROM loans l

        JOIN users u
        ON l.user_id = u.user_id

        JOIN books b
        ON l.book_id = b.book_id

        WHERE l.status = 'borrowed'
    """

    params = ()

    # الأدمن يشوف كل الاستعارات
    # العضو يشوف استعاراته فقط
    if role != "admin":

        query += " AND u.username = ?"

        params = (actor,)

    query += " ORDER BY l.loan_id DESC"

    with db() as conn:

        return conn.execute(
            query,
            params
        ).fetchall()