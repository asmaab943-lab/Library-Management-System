import tkinter as tk

from Database.schema import init_db
from GUI import LibraryApp


# إنشاء قاعدة البيانات والجداول
init_db()

# تشغيل الواجهة
root = tk.Tk()

app = LibraryApp(root)

root.mainloop()