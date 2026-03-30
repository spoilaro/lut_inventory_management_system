from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ims.db")

WINDOW_GEOMETRY = "1100x500+320+220"

FONT_LABEL = ("goudy old style", 18)
FONT_ENTRY = ("goudy old style", 15)
FONT_SEARCH = ("goudy old style", 12, "bold")
FONT_BTN = ("goudy old style", 15)

COLOR_BG = "white"
COLOR_TITLE_BG = "#0f4d7d"
COLOR_ENTRY_BG = "lightyellow"
COLOR_BTN_ADD = "#2196f3"
COLOR_BTN_UPDATE = "#4caf50"
COLOR_BTN_DELETE = "#f44336"
COLOR_BTN_CLEAR = "#607d8b"

STATUS_OPTIONS = ("Active", "Inactive")
SEARCH_OPTIONS = ("Select", "Category", "Supplier", "Name")

PRODUCT_COLUMNS = ("pid", "Category", "Supplier", "name", "price", "qty", "status")
PRODUCT_HEADINGS = {
    "pid": "P ID",
    "Category": "Category",
    "Supplier": "Supplier",
    "name": "Name",
    "price": "Price",
    "qty": "Quantity",
    "status": "Status",
}
PRODUCT_COLUMN_WIDTHS = {col: 100 for col in PRODUCT_COLUMNS}
PRODUCT_COLUMN_WIDTHS["pid"] = 90

FORM_FIELDS = [
    ("Category", 60, "var_cat"),
    ("Supplier", 110, "var_sup"),
    ("Name", 160, "var_name"),
    ("Price", 210, "var_price"),
    ("Quantity", 260, "var_qty"),
    ("Status", 310, "var_status"),
]

ACTION_BUTTONS = [
    ("Save", 10, COLOR_BTN_ADD, "add"),
    ("Update", 120, COLOR_BTN_UPDATE, "update"),
    ("Delete", 230, COLOR_BTN_DELETE, "delete"),
    ("Clear", 340, COLOR_BTN_CLEAR, "clear"),
]


class productClass:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.config(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.focus_force()

        self.cat_list: list[str] = ["Select"]
        self.sup_list: list[str] = ["Select"]
        self._cat_combobox: ttk.Combobox = None
        self._sup_combobox: ttk.Combobox = None

        self._init_variables()
        self.fetch_cat_sup()
        self._setup_ui()
        self.show()

    def _init_variables(self) -> None:
        self.var_cat = StringVar()
        self.var_sup = StringVar()
        self.var_pid = StringVar()
        self.var_name = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_status = StringVar()
        self.var_status.set(STATUS_OPTIONS[0])
        self.var_searchby = StringVar()
        self.var_searchtxt = StringVar()

    def _setup_ui(self) -> None:
        self._setup_form_section()
        self._setup_search_section()
        self._setup_product_table()

    def _setup_form_section(self) -> None:
        frame = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=10, y=10, width=450, height=480)

        Label(
            frame,
            text="Manage Product Details",
            font=FONT_LABEL,
            bg=COLOR_TITLE_BG,
            fg="white",
        ).pack(side=TOP, fill=X)

        self._setup_form_fields(frame)
        self._setup_form_buttons(frame)

    def _setup_form_fields(self, parent: Frame) -> None:
        for field_name, y, var_attr in FORM_FIELDS:
            Label(parent, text=field_name, font=FONT_LABEL, bg=COLOR_BG).place(
                x=30, y=y
            )

            entry_x = 150
            entry_width = 200

            if field_name == "Category":
                self._cat_combobox = ttk.Combobox(
                    parent,
                    textvariable=self.var_cat,
                    values=self.cat_list,
                    state="readonly",
                    justify=CENTER,
                    font=FONT_ENTRY,
                )
                self._cat_combobox.place(x=entry_x, y=y, width=entry_width)
                self._cat_combobox.current(0)
            elif field_name == "Supplier":
                self._sup_combobox = ttk.Combobox(
                    parent,
                    textvariable=self.var_sup,
                    values=self.sup_list,
                    state="readonly",
                    justify=CENTER,
                    font=FONT_ENTRY,
                )
                self._sup_combobox.place(x=entry_x, y=y, width=entry_width)
                self._sup_combobox.current(0)
            elif field_name == "Status":
                ttk.Combobox(
                    parent,
                    textvariable=self.var_status,
                    values=STATUS_OPTIONS,
                    state="readonly",
                    justify=CENTER,
                    font=FONT_ENTRY,
                ).place(x=entry_x, y=y, width=entry_width)
            else:
                Entry(
                    parent,
                    textvariable=getattr(self, var_attr),
                    font=FONT_ENTRY,
                    bg=COLOR_ENTRY_BG,
                ).place(x=entry_x, y=y, width=entry_width)

    def _setup_form_buttons(self, parent: Frame) -> None:
        for text, x, color, method_name in ACTION_BUTTONS:
            Button(
                parent,
                text=text,
                command=getattr(self, method_name),
                font=FONT_BTN,
                bg=color,
                fg="white",
                cursor="hand2",
            ).place(x=x, y=400, width=100, height=40)

    def _setup_search_section(self) -> None:
        frame = LabelFrame(
            self.root,
            text="Search Product",
            font=FONT_SEARCH,
            bd=2,
            relief=RIDGE,
            bg=COLOR_BG,
        )
        frame.place(x=480, y=10, width=600, height=80)

        ttk.Combobox(
            frame,
            textvariable=self.var_searchby,
            values=SEARCH_OPTIONS,
            state="readonly",
            justify=CENTER,
            font=FONT_ENTRY,
        ).place(x=10, y=10, width=180)
        self.var_searchby.set(SEARCH_OPTIONS[0])

        Entry(
            frame, textvariable=self.var_searchtxt, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=200, y=10)

        Button(
            frame,
            text="Search",
            command=self.search,
            font=FONT_ENTRY,
            bg=COLOR_BTN_UPDATE,
            fg="white",
            cursor="hand2",
        ).place(x=410, y=9, width=150, height=30)

    def _setup_product_table(self) -> None:
        frame = Frame(self.root, bd=3, relief=RIDGE)
        frame.place(x=480, y=100, width=600, height=390)

        scrollbar_y = Scrollbar(frame, orient=VERTICAL)
        scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)

        self.product_table = ttk.Treeview(
            frame,
            columns=PRODUCT_COLUMNS,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        scrollbar_x.pack(side=BOTTOM, fill=X)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.config(command=self.product_table.xview)
        scrollbar_y.config(command=self.product_table.yview)

        for col in PRODUCT_COLUMNS:
            self.product_table.heading(col, text=PRODUCT_HEADINGS.get(col, col.title()))
        self.product_table["show"] = "headings"

        for col, width in PRODUCT_COLUMN_WIDTHS.items():
            self.product_table.column(col, width=width)

        self.product_table.pack(fill=BOTH, expand=1)
        self.product_table.bind("<ButtonRelease-1>", self.get_data)

    def _get_db_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(database=DB_PATH)

    def fetch_cat_sup(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT name FROM category")
            cats = cur.fetchall()
            self.cat_list = ["Select"] + [cat[0] for cat in cats]

            cur.execute("SELECT name FROM supplier")
            sups = cur.fetchall()
            self.sup_list = ["Select"] + [sup[0] for sup in sups]

            con.close()

            if self._cat_combobox:
                self._cat_combobox["values"] = self.cat_list
                self._cat_combobox.current(0)
            if self._sup_combobox:
                self._sup_combobox["values"] = self.sup_list
                self._sup_combobox.current(0)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def _get_form_data(self) -> dict:
        return {
            "pid": self.var_pid.get().strip(),
            "category": self.var_cat.get(),
            "supplier": self.var_sup.get(),
            "name": self.var_name.get().strip(),
            "price": self.var_price.get().strip(),
            "qty": self.var_qty.get().strip(),
            "status": self.var_status.get(),
        }

    def _product_exists(self, cur: sqlite3.Cursor, name: str) -> bool:
        cur.execute("SELECT * FROM product WHERE name=?", (name,))
        return cur.fetchone() is not None

    def _populate_form(self, data: tuple) -> None:
        self.var_pid.set(data[0])
        self.var_cat.set(data[1])
        self.var_sup.set(data[2])
        self.var_name.set(data[3])
        self.var_price.set(data[4])
        self.var_qty.set(data[5])
        self.var_status.set(data[6])

    def add(self) -> None:
        data = self._get_form_data()

        if data["category"] in ("Select", "") or data["supplier"] in ("Select", ""):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            if self._product_exists(cur, data["name"]):
                messagebox.showerror(
                    "Error", "Product already exists", parent=self.root
                )
                con.close()
                return

            cur.execute(
                "INSERT INTO product(Category, Supplier, name, price, qty, status) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    data["category"],
                    data["supplier"],
                    data["name"],
                    data["price"],
                    data["qty"],
                    data["status"],
                ),
            )
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success", "Product Added Successfully", parent=self.root
            )
            self.clear()
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def show(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM product")
            rows = cur.fetchall()
            con.close()

            self.product_table.delete(*self.product_table.get_children())
            for row in rows:
                self.product_table.insert("", END, values=row)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def get_data(self, ev: Event) -> None:
        focus = self.product_table.focus()
        if not focus:
            return

        row = self.product_table.item(focus)["values"]
        self._populate_form(row)

    def update(self) -> None:
        data = self._get_form_data()

        if not data["pid"]:
            messagebox.showerror(
                "Error", "Select a product to update", parent=self.root
            )
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM product WHERE pid=?", (data["pid"],))
            if not cur.fetchone():
                messagebox.showerror("Error", "Invalid Product", parent=self.root)
                con.close()
                return

            cur.execute(
                "UPDATE product SET Category=?, Supplier=?, name=?, price=?, qty=?, status=? WHERE pid=?",
                (
                    data["category"],
                    data["supplier"],
                    data["name"],
                    data["price"],
                    data["qty"],
                    data["status"],
                    data["pid"],
                ),
            )
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success", "Product Updated Successfully", parent=self.root
            )
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def delete(self) -> None:
        pid = self.var_pid.get().strip()
        if not pid:
            messagebox.showerror(
                "Error", "Select a product to delete", parent=self.root
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

            cur.execute("SELECT * FROM product WHERE pid=?", (pid,))
            if not cur.fetchone():
                messagebox.showerror("Error", "Invalid Product", parent=self.root)
                con.close()
                return

            cur.execute("DELETE FROM product WHERE pid=?", (pid,))
            con.commit()
            con.close()

            messagebox.showinfo(
                "Delete", "Product Deleted Successfully", parent=self.root
            )
            self.clear()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def clear(self) -> None:
        self.var_cat.set("Select")
        self.var_sup.set("Select")
        self.var_pid.set("")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.var_status.set("Active")
        self.var_searchby.set("Select")
        self.var_searchtxt.set("")
        self.show()

    def search(self) -> None:
        search_by = self.var_searchby.get()
        search_txt = self.var_searchtxt.get().strip()

        if search_by == "Select":
            messagebox.showerror("Error", "Select Search By option", parent=self.root)
            return
        if not search_txt:
            messagebox.showerror("Error", "Search input is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute(
                "SELECT * FROM product WHERE ? LIKE ?", (search_by, f"%{search_txt}%")
            )
            rows = cur.fetchall()
            con.close()

            if rows:
                self.product_table.delete(*self.product_table.get_children())
                for row in rows:
                    self.product_table.insert("", END, values=row)
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)


if __name__ == "__main__":
    root = Tk()
    obj = productClass(root)
    root.mainloop()
