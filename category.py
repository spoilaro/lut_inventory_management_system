from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
DB_PATH = os.path.join(BASE_DIR, "ims.db")

WINDOW_GEOMETRY = "1100x500+320+220"

FONT_TITLE = ("goudy old style", 30)
FONT_LABEL = ("goudy old style", 30)
FONT_ENTRY = ("goudy old style", 18)
FONT_BTN = ("goudy old style", 15)

COLOR_BG = "white"
COLOR_TITLE_BG = "#184a45"
COLOR_BTN_ADD = "#4caf50"
COLOR_BTN_DELETE = "red"
COLOR_ENTRY_BG = "lightyellow"

IMAGES = [
    ("cat.jpg", 50, 220, 500, 250),
    ("category.jpg", 580, 220, 500, 250),
]


class categoryClass:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.config(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.focus_force()

        self.var_cat_id = StringVar()
        self.var_name = StringVar()

        self._setup_ui()
        self.show()

    def _setup_ui(self) -> None:
        self._setup_title()
        self._setup_input_section()
        self._setup_category_table()
        self._setup_images()

    def _setup_title(self) -> None:
        Label(
            self.root,
            text="Manage Product Category",
            font=FONT_TITLE,
            bg=COLOR_TITLE_BG,
            fg="white",
            bd=3,
            relief=RIDGE,
        ).pack(side=TOP, fill=X, padx=10, pady=20)

    def _setup_input_section(self) -> None:
        Label(
            self.root, text="Enter Category Name", font=FONT_LABEL, bg=COLOR_BG
        ).place(x=50, y=100)

        Entry(
            self.root, textvariable=self.var_name, bg=COLOR_ENTRY_BG, font=FONT_ENTRY
        ).place(x=50, y=170, width=300, height=30)

        Button(
            self.root,
            text="ADD",
            command=self.add,
            font=FONT_BTN,
            bg=COLOR_BTN_ADD,
            fg="white",
            cursor="hand2",
        ).place(x=360, y=170, width=150, height=30)

        Button(
            self.root,
            text="Delete",
            command=self.delete,
            font=FONT_BTN,
            bg=COLOR_BTN_DELETE,
            fg="white",
            cursor="hand2",
        ).place(x=520, y=170, width=150, height=30)

    def _setup_category_table(self) -> None:
        frame = Frame(self.root, bd=3, relief=RIDGE)
        frame.place(x=700, y=100, width=380, height=100)

        scrollbar_y = Scrollbar(frame, orient=VERTICAL)
        scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)

        columns = ("cid", "name")
        self.category_table = ttk.Treeview(
            frame,
            columns=columns,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        scrollbar_x.pack(side=BOTTOM, fill=X)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.config(command=self.category_table.xview)
        scrollbar_y.config(command=self.category_table.yview)

        self.category_table.heading("cid", text="C ID")
        self.category_table.heading("name", text="Name")
        self.category_table["show"] = "headings"
        self.category_table.column("cid", width=90)
        self.category_table.column("name", width=100)
        self.category_table.pack(fill=BOTH, expand=1)
        self.category_table.bind("<ButtonRelease-1>", self.get_data)

    def _setup_images(self) -> None:
        for filename, x, y, width, height in IMAGES:
            image_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(image_path):
                photo = Image.open(image_path)
                photo = photo.resize((width, height))
                photo = ImageTk.PhotoImage(photo)
                label = Label(self.root, image=photo, bd=2, relief=RAISED)
                label.image = photo
                label.place(x=x, y=y)

    def _get_db_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(database=DB_PATH)

    def add(self) -> None:
        name = self.var_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Category Name is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM category WHERE name=?", (name,))
            if cur.fetchone():
                messagebox.showerror(
                    "Error", "Category already exists", parent=self.root
                )
                con.close()
                return

            cur.execute("INSERT INTO category(name) VALUES(?)", (name,))
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success", "Category Added Successfully", parent=self.root
            )
            self.clear()
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def show(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM category")
            rows = cur.fetchall()
            con.close()

            self.category_table.delete(*self.category_table.get_children())
            for row in rows:
                self.category_table.insert("", END, values=row)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def get_data(self, ev: Event) -> None:
        focus = self.category_table.focus()
        if not focus:
            return

        row = self.category_table.item(focus)["values"]
        self.var_cat_id.set(row[0])
        self.var_name.set(row[1])

    def delete(self) -> None:
        cat_id = self.var_cat_id.get().strip()
        if not cat_id:
            messagebox.showerror(
                "Error", "Select a category to delete", parent=self.root
            )
            return

        confirm = messagebox.askyesno(
            "Confirm", "Do you really want to delete?", parent=self.root
        )
        if not confirm:
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM category WHERE cid=?", (cat_id,))
            if not cur.fetchone():
                messagebox.showerror("Error", "Invalid Category", parent=self.root)
                con.close()
                return

            cur.execute("DELETE FROM category WHERE cid=?", (cat_id,))
            con.commit()
            con.close()

            messagebox.showinfo(
                "Delete", "Category Deleted Successfully", parent=self.root
            )
            self.clear()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def clear(self) -> None:
        self.var_cat_id.set("")
        self.var_name.set("")
        self.show()


if __name__ == "__main__":
    root = Tk()
    obj = categoryClass(root)
    root.mainloop()
