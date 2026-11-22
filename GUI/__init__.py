
import tkinter as tk
from tkinter import ttk, messagebox

from Database.schema import init_db
from Backend import library_backend as bk

# ---------------- ألوان التصميم المستوحاة من الصورة ----------------
BG_MAIN = "#F6F1EA"       # كريمي / أوف وايت ناعم
BG_CARD = "#FFFFFF"       # أبيض للبطاقات والحقول
NAVY = "#1B2845"          # كحلي داكن للقائمة والأزرار الرئيسية
NAVY_HOVER = "#27385E"
LAVENDER = "#D8D2E9"      # بنفسجي/لافندر فاتح للأزرار الثانوية
TEXT_DARK = "#1E2430"
TEXT_MUTED = "#6B7280"
GREEN_SOFT = "#DDF3E4"
GREEN_TEXT = "#1E6F43"
RED_SOFT = "#FADDDD"
RED_TEXT = "#9E2A2B"
BORDER_COLOR = "#E2DCD2"


class LibraryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1040x650")
        self.root.minsize(900, 580)
        self.root.configure(bg=BG_MAIN)

        self.current_user = None
        self.current_role = None

        self.setup_styles()
        self.show_login_screen()

    @property
    def is_admin(self):
        return self.current_role == "admin"

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background=BG_CARD,
            foreground=TEXT_DARK,
            rowheight=32,
            fieldbackground=BG_CARD,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#EFECE6",
            foreground=NAVY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(6, 8)
        )
        style.map("Custom.Treeview.Heading", background=[("active", "#E5E0D5")])
        style.map(
            "Custom.Treeview",
            background=[("selected", LAVENDER)],
            foreground=[("selected", NAVY)]
        )

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==================== شاشة تسجيل الدخول ====================
    def show_login_screen(self):
        self.current_user = None
        self.current_role = None
        self.clear_root()

        wrapper = tk.Frame(self.root, bg=BG_MAIN)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        # الجانب الأيسر (عنوان + بطاقة زخرفية بسيطة)
        left_panel = tk.Frame(wrapper, bg=BG_MAIN)
        left_panel.pack(side="left", fill="both", expand=True, padx=(10, 20))

        tk.Label(
            left_panel,
            text="📖",
            font=("Segoe UI", 42),
            bg=BG_MAIN,
            fg=NAVY
        ).pack(anchor="w", pady=(50, 10))

        tk.Label(
            left_panel,
            text="Library\nManagement\nSystem",
            font=("Georgia", 34, "bold"),
            bg=BG_MAIN,
            fg=NAVY,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            left_panel,
            text="Read  •  Learn  •  Grow ♡",
            font=("Georgia", 12, "italic"),
            bg=BG_MAIN,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(18, 0))

        # الجانب الأيمن (بطاقة تسجيل الدخول)
        right_panel = tk.Frame(
            wrapper,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=36,
            pady=36
        )
        right_panel.pack(side="right", fill="y", padx=(20, 10))

        tk.Label(
            right_panel,
            text="Login",
            font=("Segoe UI", 24, "bold"),
            bg=BG_CARD,
            fg=NAVY
        ).pack(pady=(0, 20))

        tk.Label(
            right_panel,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD,
            fg=TEXT_DARK
        ).pack(anchor="w")

        self.username_entry = tk.Entry(
            right_panel,
            font=("Segoe UI", 11),
            bg="#FAF8F5",
            fg=TEXT_DARK,
            relief="solid",
            bd=1,
            width=28
        )
        self.username_entry.pack(ipady=7, pady=(5, 14))

        tk.Label(
            right_panel,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD,
            fg=TEXT_DARK
        ).pack(anchor="w")

        pass_row = tk.Frame(right_panel, bg=BG_CARD)
        pass_row.pack(fill="x", pady=(5, 22))

        self.password_entry = tk.Entry(
            pass_row,
            font=("Segoe UI", 11),
            bg="#FAF8F5",
            fg=TEXT_DARK,
            relief="solid",
            bd=1,
            show="*",
            width=23
        )
        self.password_entry.pack(side="left", ipady=7)

        self.show_pass_var = tk.BooleanVar(value=False)

        def toggle_pass():
            self.password_entry.config(show="" if self.show_pass_var.get() else "*")

        tk.Checkbutton(
            pass_row,
            text="👁",
            variable=self.show_pass_var,
            command=toggle_pass,
            bg=BG_CARD,
            fg=NAVY,
            activebackground=BG_CARD,
            bd=0
        ).pack(side="left", padx=(6, 0))

        login_btn = tk.Button(
            right_panel,
            text="→  Login",
            font=("Segoe UI", 11, "bold"),
            bg=NAVY,
            fg="white",
            activebackground=NAVY_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_login
        )
        login_btn.pack(fill="x", ipady=9)

        # زر سريع لتسجيل مستخدم جديد إذا أراد التجربة
        tk.Button(
            right_panel,
            text="Create Member Account",
            font=("Segoe UI", 9, "underline"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            activebackground=BG_CARD,
            bd=0,
            cursor="hand2",
            command=self.open_register_dialog
        ).pack(pady=(14, 0))

        self.password_entry.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("تنبيه", "من فضلك أدخل اسم المستخدم وكلمة المرور.")
            return

        role = bk.authenticate(username, password)
        if role:
            self.current_user = username
            self.current_role = role
            self.show_main_app()
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة.")

    def open_register_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("New Member")
        win.geometry("340x280")
        win.configure(bg=BG_MAIN)
        win.grab_set()

        tk.Label(
            win, text="Create Member Account",
            font=("Segoe UI", 14, "bold"), bg=BG_MAIN, fg=NAVY
        ).pack(pady=(18, 12))

        tk.Label(win, text="Username", bg=BG_MAIN, fg=TEXT_DARK, font=("Segoe UI", 10)).pack(anchor="w", padx=30)
        u_ent = tk.Entry(win, font=("Segoe UI", 10), bg=BG_CARD)
        u_ent.pack(fill="x", padx=30, ipady=5, pady=(2, 10))

        tk.Label(win, text="Password", bg=BG_MAIN, fg=TEXT_DARK, font=("Segoe UI", 10)).pack(anchor="w", padx=30)
        p_ent = tk.Entry(win, font=("Segoe UI", 10), bg=BG_CARD, show="*")
        p_ent.pack(fill="x", padx=30, ipady=5, pady=(2, 16))

        def save_member():
            ok, msg = bk.register_member(u_ent.get(), p_ent.get())
            if ok:
                messagebox.showinfo("تم", msg, parent=win)
                win.destroy()
            else:
                messagebox.showwarning("تنبيه", msg, parent=win)

        tk.Button(
            win, text="Save", bg=NAVY, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=save_member
        ).pack(fill="x", padx=30, ipady=7)

    # ==================== الواجهة الرئيسية ====================
    def show_main_app(self):
        self.clear_root()

        # القائمة الجانبية الكحلية
        sidebar = tk.Frame(self.root, bg=NAVY, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text=f"👤 {self.current_user}\n({self.current_role})",
            font=("Segoe UI", 10, "bold"),
            bg=NAVY,
            fg="#E2E8F0",
            justify="center"
        ).pack(pady=(24, 24))

        self.nav_buttons = {}

        def make_nav_btn(key, text, cmd):
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Segoe UI", 11, "bold"),
                bg=NAVY,
                fg="white",
                activebackground=NAVY_HOVER,
                activeforeground="white",
                bd=0,
                anchor="w",
                padx=20,
                pady=12,
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        make_nav_btn("books", "📚  Books & Authors", lambda: self.switch_page("books"))
        make_nav_btn("borrow", "🔄  Borrow & Return", lambda: self.switch_page("borrow"))

        tk.Label(
            sidebar,
            text="Knowledge\nis Power ♡",
            font=("Georgia", 11, "italic"),
            bg=NAVY,
            fg="#CBD5E1",
            justify="center"
        ).pack(side="bottom", pady=(0, 50))

        tk.Button(
            sidebar,
            text="⏻  Logout",
            font=("Segoe UI", 10),
            bg=NAVY,
            fg="#FCA5A5",
            activebackground=NAVY_HOVER,
            activeforeground="white",
            bd=0,
            anchor="w",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.show_login_screen
        ).pack(side="bottom", fill="x")

        # منطقة المحتوى الرئيسية
        self.content_area = tk.Frame(self.root, bg=BG_MAIN)
        self.content_area.pack(side="right", fill="both", expand=True)

        self.switch_page("books")

    def highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.config(bg=NAVY_HOVER)
            else:
                btn.config(bg=NAVY)

    def switch_page(self, page_name):
        self.highlight_nav(page_name)
        for w in self.content_area.winfo_children():
            w.destroy()

        if page_name == "books":
            self.build_books_page()
        elif page_name == "borrow":
            self.build_borrow_page()

    # ==================== صفحة Books & Authors ====================
    def build_books_page(self):
        pad = tk.Frame(self.content_area, bg=BG_MAIN)
        pad.pack(fill="both", expand=True, padx=28, pady=22)

        # العنوان
        header = tk.Frame(pad, bg=BG_MAIN)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text="📖  Books & Authors",
            font=("Segoe UI", 22, "bold"),
            bg=BG_MAIN,
            fg=NAVY
        ).pack(side="left")

        tk.Button(
            header,
            text="Show All",
            font=("Segoe UI", 9, "bold"),
            bg=LAVENDER,
            fg=NAVY,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.refresh_books_table
        ).pack(side="right")

        # شريط البحث
        search_frame = tk.Frame(pad, bg=BG_MAIN)
        search_frame.pack(fill="x", pady=(0, 14))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 11),
            bg=BG_CARD,
            fg=TEXT_DARK,
            relief="solid",
            bd=1
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.handle_search())

        tk.Button(
            search_frame,
            text="🔍  Search",
            font=("Segoe UI", 10, "bold"),
            bg=NAVY,
            fg="white",
            activebackground=NAVY_HOVER,
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.handle_search
        ).pack(side="right")

        # جدول الكتب
        table_card = tk.Frame(
            pad,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        table_card.pack(fill="both", expand=True, pady=(0, 16))

        columns = ("id", "title", "author", "category", "available")
        self.books_tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        headings = {
            "id": ("ID", 60, "center"),
            "title": ("Title", 250, "w"),
            "author": ("Author", 180, "w"),
            "category": ("Category", 130, "center"),
            "available": ("Available", 100, "center"),
        }
        for col, (text, width, anchor) in headings.items():
            self.books_tree.heading(col, text=text)
            self.books_tree.column(col, width=width, anchor=anchor)

        self.books_tree.tag_configure("yes", background=GREEN_SOFT, foreground=GREEN_TEXT)
        self.books_tree.tag_configure("no", background=RED_SOFT, foreground=RED_TEXT)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        self.books_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # أزرار الإضافة والحذف في الأسفل (للأدمن فقط)
        if self.is_admin:
            bottom_bar = tk.Frame(pad, bg=BG_MAIN)
            bottom_bar.pack(fill="x")

            tk.Button(
                bottom_bar,
                text="+  Add Book",
                font=("Segoe UI", 10, "bold"),
                bg=NAVY,
                fg="white",
                activebackground=NAVY_HOVER,
                activeforeground="white",
                relief="flat",
                padx=18,
                pady=8,
                cursor="hand2",
                command=self.open_add_book_dialog
            ).pack(side="left", padx=(0, 10))

            tk.Button(
                bottom_bar,
                text="🗑  Delete",
                font=("Segoe UI", 10, "bold"),
                bg=RED_SOFT,
                fg=RED_TEXT,
                activebackground="#F5C2C2",
                relief="flat",
                padx=18,
                pady=8,
                cursor="hand2",
                command=self.handle_delete_book
            ).pack(side="right")

        self.refresh_books_table()

    def populate_books_tree(self, books_list):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        for b in books_list:
            avail_text = "Yes" if b["available"] else "No"
            tag = "yes" if b["available"] else "no"
            self.books_tree.insert(
                "",
                "end",
                values=(b["id"], b["title"], b["author"], b["category"], avail_text),
                tags=(tag,)
            )

    def refresh_books_table(self):
        self.populate_books_tree(bk.display_books())

    def handle_search(self):
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_books_table()
            return
        self.populate_books_tree(bk.search_book(query))

    def open_add_book_dialog(self):
        if not self.is_admin:
            return

        win = tk.Toplevel(self.root)
        win.title("Add Book")
        win.geometry("360x340")
        win.configure(bg=BG_MAIN)
        win.grab_set()

        tk.Label(
            win, text="+ Add New Book",
            font=("Segoe UI", 14, "bold"), bg=BG_MAIN, fg=NAVY
        ).pack(pady=(16, 10))

        def field(label_text, default_val=""):
            tk.Label(win, text=label_text, bg=BG_MAIN, fg=TEXT_DARK, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=32)
            ent = tk.Entry(win, font=("Segoe UI", 10), bg=BG_CARD)
            if default_val:
                ent.insert(0, default_val)
            ent.pack(fill="x", padx=32, ipady=4, pady=(2, 8))
            return ent

        id_ent = field("Book ID (optional)", str(bk.get_next_book_id()))
        title_ent = field("Title")
        author_ent = field("Author")
        cat_ent = field("Category", "رواية")

        def submit():
            title = title_ent.get().strip()
            author = author_ent.get().strip()
            category = cat_ent.get().strip()
            raw_id = id_ent.get().strip()

            if not title or not author or not category:
                messagebox.showwarning("تنبيه", "من فضلك أدخل عنوان الكتاب والمؤلف والتصنيف.", parent=win)
                return

            try:
                book_id = int(raw_id) if raw_id else bk.get_next_book_id()
            except ValueError:
                messagebox.showwarning("تنبيه", "Book ID يجب أن يكون رقماً.", parent=win)
                return

            ok, msg = bk.add_book(self.current_user, book_id, title, author, category)
            messagebox.showinfo("النتيجة", msg, parent=win)
            if ok:
                win.destroy()
                self.refresh_books_table()

        tk.Button(
            win, text="Save Book", bg=NAVY, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=submit
        ).pack(fill="x", padx=32, pady=(8, 0), ipady=7)

    def handle_delete_book(self):
        if not self.is_admin:
            return

        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر كتاباً من الجدول أولاً لحذفه.")
            return

        values = self.books_tree.item(selected[0], "values")
        book_id = int(values[0])
        title = values[1]

        confirm = messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف الكتاب:\n{title} (ID: {book_id})؟")
        if not confirm:
            return

        ok, msg = bk.delete_book(self.current_user, book_id)
        messagebox.showinfo("النتيجة", msg)
        self.refresh_books_table()

    # ==================== صفحة Borrow & Return ====================
    def build_borrow_page(self):
        pad = tk.Frame(self.content_area, bg=BG_MAIN)
        pad.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(
            pad,
            text="🔄  Borrow & Return",
            font=("Segoe UI", 22, "bold"),
            bg=BG_MAIN,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 16))

        # بطاقة اختيار العضو والكتاب
        form_card = tk.Frame(
            pad,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=20,
            pady=18
        )
        form_card.pack(fill="x", pady=(0, 18))

        # الأدمن يختار من الأعضاء، والـ Member مقفول على اسمه فقط
        if self.is_admin:
            member_names = bk.get_member_names()
        else:
            member_names = [self.current_user]

        books_list = bk.display_books()
        book_labels = [f"{b['id']} - {b['title']}" for b in books_list]

        top_row = tk.Frame(form_card, bg=BG_CARD)
        top_row.pack(fill="x", pady=(0, 14))

        # عمود العضو
        left_col = tk.Frame(top_row, bg=BG_CARD)
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(
            left_col, text="👤  Member:",
            font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=NAVY
        ).pack(anchor="w", pady=(0, 4))

        self.member_combo = ttk.Combobox(
            left_col, values=member_names, font=("Segoe UI", 10), state="readonly"
        )
        if member_names:
            self.member_combo.set(member_names[0])
        self.member_combo.pack(fill="x", ipady=4)

        # عمود الكتاب
        right_col = tk.Frame(top_row, bg=BG_CARD)
        right_col.pack(side="right", fill="x", expand=True, padx=(12, 0))

        tk.Label(
            right_col, text="📖  Book:",
            font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=NAVY
        ).pack(anchor="w", pady=(0, 4))

        self.book_combo = ttk.Combobox(
            right_col, values=book_labels, font=("Segoe UI", 10), state="normal"
        )
        if book_labels:
            self.book_combo.set(book_labels[0])
        self.book_combo.pack(fill="x", ipady=4)

        # أزرار الاستعارة والإرجاع
        btn_row = tk.Frame(form_card, bg=BG_CARD)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="📘  Borrow Book",
            font=("Segoe UI", 10, "bold"),
            bg=NAVY,
            fg="white",
            activebackground=NAVY_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_borrow
        ).pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)

        tk.Button(
            btn_row,
            text="↩  Return Book",
            font=("Segoe UI", 10, "bold"),
            bg=LAVENDER,
            fg=NAVY,
            activebackground="#C5BCDC",
            relief="flat",
            cursor="hand2",
            command=self.handle_return
        ).pack(side="right", fill="x", expand=True, padx=(10, 0), ipady=8)

        # جدول الاستعارات الحالية
        loans_title = "🕒  Current Loans" if self.is_admin else "🕒  My Loans"
        tk.Label(
            pad,
            text=loans_title,
            font=("Segoe UI", 13, "bold"),
            bg=BG_MAIN,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 8))

        loans_card = tk.Frame(
            pad,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        loans_card.pack(fill="both", expand=True)

        self.loans_tree = ttk.Treeview(
            loans_card,
            columns=("member", "book", "borrow_date", "due_date"),
            show="headings",
            style="Custom.Treeview"
        )
        for col, title, w, anc in [
            ("member", "Member", 160, "w"),
            ("book", "Book", 250, "w"),
            ("borrow_date", "Borrow Date", 130, "center"),
            ("due_date", "Due Date", 130, "center"),
        ]:
            self.loans_tree.heading(col, text=title)
            self.loans_tree.column(col, width=w, anchor=anc)

        self.loans_tree.pack(fill="both", expand=True)
        self.refresh_loans_table()

    def parse_book_id(self):
        val = self.book_combo.get().strip()
        if not val:
            return None
        # يدعم صيغة "1 - Title" أو كتابة الرقم مباشرة "1"
        part = val.split("-", 1)[0].strip()
        try:
            return int(part)
        except ValueError:
            return None

    def refresh_loans_table(self):
        for item in self.loans_tree.get_children():
            self.loans_tree.delete(item)
        for member, title, b_date, d_date, _ in bk.get_current_loans(self.current_user):
            self.loans_tree.insert("", "end", values=(member, title, b_date, d_date))

    def handle_borrow(self):
        member = self.member_combo.get().strip()
        book_id = self.parse_book_id()

        if not member or book_id is None:
            messagebox.showwarning("تنبيه", "اختر العضو والكتاب بشكل صحيح.")
            return

        ok, msg = bk.borrow_book(self.current_user, member, book_id)
        messagebox.showinfo("النتيجة", msg)
        self.refresh_loans_table()

    def handle_return(self):
        member = self.member_combo.get().strip()
        book_id = self.parse_book_id()

        if not member or book_id is None:
            messagebox.showwarning("تنبيه", "اختر العضو والكتاب بشكل صحيح.")
            return

        ok, msg = bk.return_book(self.current_user, member, book_id)
        messagebox.showinfo("النتيجة", msg)
        self.refresh_loans_table()


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()