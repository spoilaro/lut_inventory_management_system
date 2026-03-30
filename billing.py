from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import time
import os
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
BILL_DIR = os.path.join(BASE_DIR, "bill")
DB_PATH = os.path.join(BASE_DIR, "ims.db")

os.makedirs(BILL_DIR, exist_ok=True)

WINDOW_GEOMETRY = "1350x700+110+80"

FONT_TITLE = ("times new roman", 40, "bold")
FONT_SECTION = ("goudy old style", 20, "bold")
FONT_LABEL = ("times new roman", 15)
FONT_ENTRY = ("times new roman", 15)
FONT_BTN = ("goudy old style", 15, "bold")
FONT_CALC = ("arial", 15, "bold")

COLOR_BG = "white"
COLOR_TITLE_BG = "#010c48"
COLOR_FOOTER_BG = "#4d636d"
COLOR_BILL_TITLE_BG = "#262626"
COLOR_ENTRY_BG = "lightyellow"
COLOR_BTN_SEARCH = "#2196f3"
COLOR_BTN_SHOW_ALL = "#083531"
COLOR_BTN_LOGOUT = "yellow"
COLOR_DISCOUNT_BG = "#8bc34a"
COLOR_AMOUNT_BG = "#3f51b5"
COLOR_NETPAY_BG = "#607d8b"
COLOR_CART_TITLE_BG = "lightgray"
COLOR_CUSTOMER_BG = "lightgray"

BILL_COMPANY = "XYZ-Inventory"
BILL_PHONE = "9899459288"
BILL_ADDRESS = "Delhi-110053"
DISCOUNT_RATE = 0.05

CALC_BUTTONS = [
    ("7", 1, 0),
    ("8", 1, 1),
    ("9", 1, 2),
    ("+", 1, 3),
    ("4", 2, 0),
    ("5", 2, 1),
    ("6", 2, 2),
    ("-", 2, 3),
    ("1", 3, 0),
    ("2", 3, 1),
    ("3", 3, 2),
    ("*", 3, 3),
    ("0", 4, 0),
    ("C", 4, 1),
    ("=", 4, 2),
    ("/", 4, 3),
]


class billClass:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.resizable(False, False)
        self.root.config(bg=COLOR_BG)

        self.cart_list: list = []
        self.is_print_ready: bool = False
        self.invoice: int = 0

        self._init_variables()
        self._setup_ui()
        self.show()
        self._update_clock()

    def _init_variables(self) -> None:
        self.var_search = StringVar()
        self.var_cal_input = StringVar()
        self.var_cname = StringVar()
        self.var_contact = StringVar()
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_stock = StringVar()

    def _setup_ui(self) -> None:
        self._setup_header()
        self._setup_product_section()
        self._setup_customer_section()
        self._setup_cart_section()
        self._setup_product_input()
        self._setup_billing_section()
        self._setup_billing_buttons()

    def _setup_header(self) -> None:
        self.icon_title = PhotoImage(file=os.path.join(IMAGE_DIR, "logo1.png"))
        Label(
            self.root,
            text="Inventory Management System",
            image=self.icon_title,
            compound=LEFT,
            font=FONT_TITLE,
            bg=COLOR_TITLE_BG,
            fg="white",
            anchor="w",
            padx=20,
        ).place(x=0, y=0, relwidth=1, height=70)

        Button(
            self.root,
            text="Logout",
            font=("times new roman", 15, "bold"),
            bg=COLOR_BTN_LOGOUT,
            cursor="hand2",
        ).place(x=1150, y=10, height=50, width=150)

        self.lbl_clock = Label(
            self.root,
            text="Welcome to Inventory Management System\t\t Date: DD:MM:YYYY\t\t Time: HH:MM:SS",
            font=FONT_LABEL,
            bg=COLOR_FOOTER_BG,
            fg="white",
        )
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)

    def _setup_product_section(self) -> None:
        frame = Frame(self.root, bd=4, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=6, y=110, width=410, height=550)

        Label(
            frame,
            text="All Products",
            font=FONT_SECTION,
            bg=COLOR_BILL_TITLE_BG,
            fg="white",
        ).pack(side=TOP, fill=X)

        search_frame = Frame(frame, bd=2, relief=RIDGE, bg=COLOR_BG)
        search_frame.place(x=2, y=42, width=398, height=90)

        Label(
            search_frame,
            text="Search Product | By Name",
            font=FONT_LABEL,
            bg=COLOR_BG,
            fg="green",
        ).place(x=2, y=5)

        Label(search_frame, text="Product Name", font=FONT_LABEL, bg=COLOR_BG).place(
            x=2, y=45
        )

        Entry(
            search_frame,
            textvariable=self.var_search,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
        ).place(x=128, y=47, width=150, height=22)

        Button(
            search_frame,
            text="Search",
            command=self.search,
            font=FONT_BTN,
            bg=COLOR_BTN_SEARCH,
            fg="white",
            cursor="hand2",
        ).place(x=285, y=45, width=100, height=25)

        Button(
            search_frame,
            text="Show All",
            command=self.show,
            font=FONT_BTN,
            bg=COLOR_BTN_SHOW_ALL,
            fg="white",
            cursor="hand2",
        ).place(x=285, y=10, width=100, height=25)

        self._setup_product_table(frame)

        Label(
            frame,
            text="Note: 'Enter 0 Quantity to remove product from the Cart'",
            font=("goudy old style", 12),
            anchor="w",
            bg=COLOR_BG,
            fg="red",
        ).pack(side=BOTTOM, fill=X)

    def _setup_product_table(self, parent: Frame) -> None:
        table_frame = Frame(parent, bd=3, relief=RIDGE)
        table_frame.place(x=2, y=140, width=398, height=375)

        scrollbar_y = Scrollbar(table_frame, orient=VERTICAL)
        scrollbar_x = Scrollbar(table_frame, orient=HORIZONTAL)

        columns = ("pid", "name", "price", "qty", "status")
        self.product_table = ttk.Treeview(
            table_frame,
            columns=columns,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        scrollbar_x.pack(side=BOTTOM, fill=X)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.config(command=self.product_table.xview)
        scrollbar_y.config(command=self.product_table.yview)

        self._configure_table_columns(
            self.product_table,
            columns,
            {"pid": 40, "name": 100, "price": 100, "qty": 40, "status": 90},
        )

        self.product_table.pack(fill=BOTH, expand=1)
        self.product_table.bind("<ButtonRelease-1>", self.get_data)

    def _configure_table_columns(
        self, table: ttk.Treeview, columns: tuple, widths: dict
    ) -> None:
        headings = {
            "pid": "P ID",
            "name": "Name",
            "price": "Price",
            "qty": "Quantity",
            "status": "Status",
        }
        for col in columns:
            table.heading(col, text=headings.get(col, col.title()))
        table["show"] = "headings"
        for col, width in widths.items():
            table.column(col, width=width)

    def _setup_customer_section(self) -> None:
        frame = Frame(self.root, bd=4, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=420, y=110, width=530, height=70)

        Label(
            frame, text="Customer Details", font=FONT_LABEL, bg=COLOR_CUSTOMER_BG
        ).pack(side=TOP, fill=X)

        Label(frame, text="Name", font=FONT_LABEL, bg=COLOR_BG).place(x=5, y=35)
        Entry(
            frame, textvariable=self.var_cname, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=80, y=35, width=180)

        Label(frame, text="Contact No.", font=FONT_LABEL, bg=COLOR_BG).place(
            x=270, y=35
        )
        Entry(
            frame, textvariable=self.var_contact, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=380, y=35, width=140)

    def _setup_cart_section(self) -> None:
        cal_cart_frame = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        cal_cart_frame.place(x=420, y=190, width=530, height=360)

        self._setup_calculator(cal_cart_frame)
        self._setup_cart_table(cal_cart_frame)

    def _setup_calculator(self, parent: Frame) -> None:
        calc_frame = Frame(parent, bd=9, relief=RIDGE, bg=COLOR_BG)
        calc_frame.place(x=5, y=10, width=268, height=340)

        Entry(
            calc_frame,
            textvariable=self.var_cal_input,
            font=FONT_CALC,
            width=21,
            bd=10,
            relief=GROOVE,
            state="readonly",
            justify=RIGHT,
        ).grid(row=0, columnspan=4)

        for text, row, col in CALC_BUTTONS:
            if text == "C":
                cmd = self.clear_cal
            elif text == "=":
                cmd = self.perform_cal
            else:
                cmd = lambda t=text: self.get_input(t)

            Button(
                calc_frame,
                text=text,
                font=FONT_CALC,
                command=cmd,
                bd=5,
                width=4,
                pady=10 if row < 4 else 15,
                cursor="hand2",
            ).grid(row=row, column=col)

    def _setup_cart_table(self, parent: Frame) -> None:
        frame = Frame(parent, bd=3, relief=RIDGE)
        frame.place(x=280, y=8, width=245, height=342)

        self.cart_title = Label(
            frame,
            text="Cart \t Total Products: [0]",
            font=FONT_BTN,
            bg=COLOR_CUSTOMER_BG,
        )
        self.cart_title.pack(side=TOP, fill=X)

        scrollbar_y = Scrollbar(frame, orient=VERTICAL)
        scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)

        columns = ("pid", "name", "price", "qty")
        self.cart_table = ttk.Treeview(
            frame,
            columns=columns,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        scrollbar_x.pack(side=BOTTOM, fill=X)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.config(command=self.cart_table.xview)
        scrollbar_y.config(command=self.cart_table.yview)

        self._configure_table_columns(
            self.cart_table, columns, {"pid": 40, "name": 100, "price": 90, "qty": 30}
        )

        self.cart_table.pack(fill=BOTH, expand=1)
        self.cart_table.bind("<ButtonRelease-1>", self.get_data_cart)

    def _setup_product_input(self) -> None:
        frame = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=420, y=550, width=530, height=110)

        Label(frame, text="Product Name", font=FONT_LABEL, bg=COLOR_BG).place(x=5, y=5)
        Entry(
            frame,
            textvariable=self.var_pname,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            state="readonly",
        ).place(x=5, y=35, width=190, height=22)

        Label(frame, text="Price Per Qty", font=FONT_LABEL, bg=COLOR_BG).place(
            x=230, y=5
        )
        Entry(
            frame,
            textvariable=self.var_price,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            state="readonly",
        ).place(x=230, y=35, width=150, height=22)

        Label(frame, text="Quantity", font=FONT_LABEL, bg=COLOR_BG).place(x=390, y=5)
        Entry(
            frame, textvariable=self.var_qty, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=390, y=35, width=120, height=22)

        self.lbl_in_stock = Label(frame, text="In Stock", font=FONT_LABEL, bg=COLOR_BG)
        self.lbl_in_stock.place(x=5, y=70)

        Button(
            frame,
            text="Clear",
            command=self.clear_cart,
            font=FONT_BTN,
            bg="lightgray",
            cursor="hand2",
        ).place(x=180, y=70, width=150, height=30)

        Button(
            frame,
            text="Add | Update",
            command=self.add_update_cart,
            font=FONT_BTN,
            bg="orange",
            cursor="hand2",
        ).place(x=340, y=70, width=180, height=30)

    def _setup_billing_section(self) -> None:
        frame = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=953, y=110, width=400, height=410)

        Label(
            frame,
            text="Customer Bill Area",
            font=FONT_SECTION,
            bg=COLOR_BILL_TITLE_BG,
            fg="white",
        ).pack(side=TOP, fill=X)

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.txt_bill_area = Text(
            frame, bg=COLOR_ENTRY_BG, yscrollcommand=scrollbar.set
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.txt_bill_area.yview)
        self.txt_bill_area.pack(fill=BOTH, expand=1)

    def _setup_billing_buttons(self) -> None:
        frame = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        frame.place(x=953, y=520, width=400, height=140)

        self.lbl_amount = Label(
            frame,
            text="Bill Amount\n[0]",
            font=FONT_BTN,
            bg=COLOR_AMOUNT_BG,
            fg="white",
        )
        self.lbl_amount.place(x=2, y=5, width=120, height=70)

        self.lbl_discount = Label(
            frame,
            text="Discount\n[5%]",
            font=FONT_BTN,
            bg=COLOR_DISCOUNT_BG,
            fg="white",
        )
        self.lbl_discount.place(x=124, y=5, width=120, height=70)

        self.lbl_net_pay = Label(
            frame, text="Net Pay\n[0]", font=FONT_BTN, bg=COLOR_NETPAY_BG, fg="white"
        )
        self.lbl_net_pay.place(x=246, y=5, width=160, height=70)

        Button(
            frame,
            text="Print",
            command=self.print_bill,
            font=FONT_BTN,
            bg="lightgreen",
            cursor="hand2",
        ).place(x=2, y=80, width=120, height=50)

        Button(
            frame,
            text="Clear All",
            command=self.clear_all,
            font=FONT_BTN,
            bg="gray",
            cursor="hand2",
        ).place(x=124, y=80, width=120, height=50)

        Button(
            frame,
            text="Generate Bill",
            command=self.generate_bill,
            font=FONT_BTN,
            bg="#009688",
            cursor="hand2",
        ).place(x=246, y=80, width=160, height=50)

    def _get_db_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(database=DB_PATH)

    def _fetch_active_products(
        self, cur: sqlite3.Cursor, search_term: str = None
    ) -> list:
        if search_term:
            cur.execute(
                "SELECT pid, name, price, qty, status FROM product WHERE name LIKE ?",
                (f"%{search_term}%",),
            )
        else:
            cur.execute(
                "SELECT pid, name, price, qty, status FROM product WHERE status='Active'"
            )
        return cur.fetchall()

    def _update_product_table(self, rows: list) -> None:
        self.product_table.delete(*self.product_table.get_children())
        for row in rows:
            self.product_table.insert("", END, values=row)

    def get_input(self, num: str) -> None:
        current = self.var_cal_input.get()
        self.var_cal_input.set(current + str(num))

    def clear_cal(self) -> None:
        self.var_cal_input.set("")

    def perform_cal(self) -> None:
        try:
            result = self.var_cal_input.get()
            self.var_cal_input.set(eval(result))
        except (SyntaxError, ZeroDivisionError, NameError):
            messagebox.showerror("Error", "Invalid expression", parent=self.root)

    def show(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()
            rows = self._fetch_active_products(cur)
            self._update_product_table(rows)
            con.close()
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def search(self) -> None:
        search_term = self.var_search.get().strip()
        if not search_term:
            messagebox.showerror("Error", "Search input is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()
            rows = self._fetch_active_products(cur, search_term)

            if rows:
                self._update_product_table(rows)
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)
            con.close()
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def get_data(self, ev: Event) -> None:
        focus = self.product_table.focus()
        if not focus:
            return
        row = self.product_table.item(focus)["values"]
        self.var_pid.set(row[0])
        self.var_pname.set(row[1])
        self.var_price.set(row[2])
        self.lbl_in_stock.config(text=f"In Stock [{row[3]}]")
        self.var_stock.set(row[3])
        self.var_qty.set("1")

    def get_data_cart(self, ev: Event) -> None:
        focus = self.cart_table.focus()
        if not focus:
            return
        row = self.cart_table.item(focus)["values"]
        self.var_pid.set(row[0])
        self.var_pname.set(row[1])
        self.var_price.set(row[2])
        self.var_qty.set(row[3])
        self.lbl_in_stock.config(text=f"In Stock [{row[4]}]")
        self.var_stock.set(row[4])

    def add_update_cart(self) -> None:
        if not self.var_pid.get():
            messagebox.showerror(
                "Error", "Please select product from the list", parent=self.root
            )
            return
        if not self.var_qty.get():
            messagebox.showerror("Error", "Quantity is required", parent=self.root)
            return

        try:
            qty = int(self.var_qty.get())
            stock = int(self.var_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Quantity", parent=self.root)
            return

        if qty > stock:
            messagebox.showerror("Error", "Invalid Quantity", parent=self.root)
            return

        cart_data = [
            self.var_pid.get(),
            self.var_pname.get(),
            self.var_price.get(),
            self.var_qty.get(),
            self.var_stock.get(),
        ]

        for idx, row in enumerate(self.cart_list):
            if self.var_pid.get() == row[0]:
                if qty == 0:
                    self.cart_list.pop(idx)
                else:
                    self.cart_list[idx][3] = self.var_qty.get()
                self.show_cart()
                self.bill_update()
                return

        self.cart_list.append(cart_data)
        self.show_cart()
        self.bill_update()

    def bill_update(self) -> None:
        bill_amount = sum(float(row[2]) * int(row[3]) for row in self.cart_list)
        discount = bill_amount * DISCOUNT_RATE
        net_pay = bill_amount - discount

        self.lbl_amount.config(text=f"Bill Amount\n{bill_amount:.2f}")
        self.lbl_net_pay.config(text=f"Net Pay\n{net_pay:.2f}")
        self.cart_title.config(text=f"Cart \t Total Products: [{len(self.cart_list)}]")

    def show_cart(self) -> None:
        try:
            self.cart_table.delete(*self.cart_table.get_children())
            for row in self.cart_list:
                self.cart_table.insert("", END, values=row)
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def generate_bill(self) -> None:
        if not self.var_cname.get() or not self.var_contact.get():
            messagebox.showerror(
                "Error", "Customer Details are required", parent=self.root
            )
            return
        if not self.cart_list:
            messagebox.showerror(
                "Error", "Please add product to the Cart!!!", parent=self.root
            )
            return

        self.invoice = int(time.strftime("%H%M%S")) + int(time.strftime("%d%m%Y"))
        bill_amount = sum(float(row[2]) * int(row[3]) for row in self.cart_list)
        discount = bill_amount * DISCOUNT_RATE
        net_pay = bill_amount - discount

        self._generate_bill_content(self.invoice, bill_amount, discount, net_pay)
        self._save_bill()
        self._update_inventory()
        self.show()

        messagebox.showinfo("Saved", "Bill has been generated", parent=self.root)
        self.is_print_ready = True

    def _generate_bill_content(
        self, invoice: int, bill_amount: float, discount: float, net_pay: float
    ) -> None:
        separator = "=" * 46

        header = f"""
\t\t{BILL_COMPANY}
\t Phone No. {BILL_PHONE}, {BILL_ADDRESS}
{separator}
 Customer Name: {self.var_cname.get()}
 Ph. no.: {self.var_contact.get()}
 Bill No. {invoice}\t\t\tDate: {time.strftime("%d/%m/%Y")}
{separator}
 Product Name\t\t\tQTY\tPrice
{separator}
"""
        self.txt_bill_area.delete("1.0", END)
        self.txt_bill_area.insert(END, header)

        for row in self.cart_list:
            price = float(row[2]) * int(row[3])
            self.txt_bill_area.insert(END, f"\n {row[1]}\t\t\t{row[3]}\tRs.{price:.2f}")

        footer = f"""
{separator}
 Bill Amount\t\t\t\tRs.{bill_amount:.2f}
 Discount\t\t\t\tRs.{discount:.2f}
 Net Pay\t\t\t\tRs.{net_pay:.2f}
{separator}
"""
        self.txt_bill_area.insert(END, footer)

    def _save_bill(self) -> None:
        bill_path = os.path.join(BILL_DIR, f"{self.invoice}.txt")
        with open(bill_path, "w") as fp:
            fp.write(self.txt_bill_area.get("1.0", END))

    def _update_inventory(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()

            for row in self.cart_list:
                pid = row[0]
                stock = int(row[4])
                qty = int(row[3])
                new_stock = stock - qty
                status = "Inactive" if new_stock == 0 else "Active"

                cur.execute(
                    "UPDATE product SET qty=?, status=? WHERE pid=?",
                    (new_stock, status, pid),
                )

            con.commit()
            con.close()
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def clear_cart(self) -> None:
        self.var_pid.set("")
        self.var_pname.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.lbl_in_stock.config(text="In Stock")
        self.var_stock.set("")

    def clear_all(self) -> None:
        self.cart_list.clear()
        self.clear_cart()
        self.show()
        self.show_cart()
        self.var_cname.set("")
        self.var_contact.set("")
        self.var_search.set("")
        self.is_print_ready = False
        self.txt_bill_area.delete("1.0", END)
        self.cart_title.config(text="Cart \t Total Products: [0]")

    def _update_clock(self) -> None:
        current_time = time.strftime("%I:%M:%S")
        current_date = time.strftime("%d-%m-%Y")
        self.lbl_clock.config(
            text=f"Welcome to Inventory Management System\t\t Date: {current_date}\t\t Time: {current_time}"
        )
        self.lbl_clock.after(200, self._update_clock)

    def print_bill(self) -> None:
        if not self.is_print_ready:
            messagebox.showinfo(
                "Print", "Please generate bill to print the receipt", parent=self.root
            )
            return

        messagebox.showinfo("Print", "Please wait while printing", parent=self.root)
        temp_file = tempfile.mktemp(".txt")
        with open(temp_file, "w") as fp:
            fp.write(self.txt_bill_area.get("1.0", END))
        os.startfile(temp_file, "print")


if __name__ == "__main__":
    root = Tk()
    obj = billClass(root)
    root.mainloop()
